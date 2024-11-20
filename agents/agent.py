# pylint: disable=print-used,no-self-use

import datetime
import operator
import os
from typing import Annotated, TypedDict
from elasticapm import capture_span
from dotenv import load_dotenv
from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from langchain_openai import AzureChatOpenAI

from agents.tools.flights_finder import flights_finder
from agents.tools.hotels_finder import hotels_finder

from langchain_core.runnables.config import RunnableConfig


# Load environment variables
load_dotenv()

CURRENT_YEAR = datetime.datetime.now().year


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]


TOOLS_SYSTEM_PROMPT = f"""You are a smart travel agency. Use the tools to look up information.
You are allowed to make multiple calls (either together or in sequence).
Only look up information when you are sure of what you want.
The current year is {CURRENT_YEAR}.
If you need to look up some information before asking a follow-up question, you are allowed to do that!
Always include prices, currencies, and links where possible.
"""

EMAILS_SYSTEM_PROMPT = """Your task is to convert structured markdown-like text into a valid HTML email body.

Do not include a 
html preamble in your response.
The output should be in proper HTML format, ready to be used as the body of an email.
"""

TOOLS = [flights_finder, hotels_finder]


class Agent:
    def __init__(self):
        # Initialize tools
        self._tools = {t.name: t for t in TOOLS}
        self._tools_llm = AzureChatOpenAI(
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            api_version="2024-02-01",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        ).bind_tools(TOOLS)

        # Build the state graph
        builder = StateGraph(AgentState)
        builder.add_node("call_tools_llm", self.call_tools_llm)
        builder.add_node("invoke_tools", self.invoke_tools)
        builder.add_node("email_sender", self.email_sender)
        builder.set_entry_point("call_tools_llm")

        builder.add_conditional_edges(
        "call_tools_llm", Agent.exists_action, {"more_tools": "invoke_tools", "email_sender": "email_sender"}
        )

        builder.add_edge("invoke_tools", "call_tools_llm")
        builder.add_edge("email_sender", END)
        config = RunnableConfig(recursion_limit=10)
        print(config)
        memory = MemorySaver()
        self.graph = builder.compile(checkpointer=memory, interrupt_before=["email_sender"])

        print(self.graph.get_graph().draw_mermaid())

    @staticmethod
    def exists_action(state: AgentState):
        """Check whether more tools need to be called or proceed to send email."""
        result = state["messages"][-1]
        print(f"Evaluating exists_action: {len(result.tool_calls)} tool calls remaining")
        return "more_tools" if len(result.tool_calls) > 0 else "email_sender"

    def email_sender(self, state: AgentState):
        """Send an email using the content from the model's response."""
        print("Sending email...")

        try:
            # Instrumentación APM
            with capture_span("send_email", "email"):
                last_message = state["messages"][-1]
                email_message = [SystemMessage(content=EMAILS_SYSTEM_PROMPT), HumanMessage(content=last_message.content)]

                # Generate email body
                email_llm = AzureChatOpenAI(
                    api_key=os.getenv("AZURE_OPENAI_KEY"),
                    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
                )
                email_response = email_llm.invoke(email_message)

                # Create SendGrid email
                message = Mail(
                    from_email=os.environ["FROM_EMAIL"],
                    to_emails=os.environ["TO_EMAIL"],
                    subject=os.environ["EMAIL_SUBJECT"],
                    html_content=email_response.content,
                )
                sg = SendGridAPIClient(os.environ.get("SENDGRID_API_KEY"))
                response = sg.send(message)

                # Log response
                print(f"Email sent! Status: {response.status_code}")
        except Exception as e:
            print(f"Error sending email: {str(e)}")

    def call_tools_llm(self, state: AgentState):
        """Call tools using the LLM."""
        print("Calling tools...")
        messages = [SystemMessage(content=TOOLS_SYSTEM_PROMPT)] + state["messages"]
        message = self._tools_llm.invoke(messages)
        return {"messages": [message]}


    def invoke_tools(self, state: AgentState):
        """Invoke tools and process the results."""
        tool_calls = state["messages"][-1].tool_calls
        results = []

        for t in tool_calls:
            try:
                # Instrumentación APM
                with capture_span(f"tool_call_{t['name']}", "tool", labels={"tool_name": t["name"], "args": str(t["args"])}):
                    start_time = datetime.datetime.now()
                    print(f"Invoking tool {t['name']} with args: {t['args']}")
                    if t["name"] not in self._tools:
                        result = "Invalid tool name. Retry."
                    else:
                        result = self._tools[t["name"]].invoke(t["args"])
                    end_time = datetime.datetime.now()
                    print(f"Tool {t['name']} responded in {end_time - start_time}: {result}")
                    results.append(ToolMessage(tool_call_id=t["id"], name=t["name"], content=str(result)))
            except Exception as e:
                print(f"Error invoking tool {t['name']}: {str(e)}")
                results.append(ToolMessage(tool_call_id=t["id"], name=t["name"], content=f"Error: {str(e)}"))

        return {"messages": results}

