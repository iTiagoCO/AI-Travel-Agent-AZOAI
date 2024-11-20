# pylint: disable = invalid-name
import os
import uuid
from elasticapm.contrib.flask import ElasticAPM
from flask import Flask

import streamlit as st
from langchain_core.messages import HumanMessage

from agents.agent import Agent

# Initialize the Flask app before using it
app = Flask(__name__)

# Error handler should be placed after app initialization
@app.errorhandler(Exception)
def handle_exception(e):
    # Elastic APM will automatically capture this exception
    return {"error": str(e)}, 500

# Configuración de Elastic APM
app.config['ELASTIC_APM'] = {
    'SERVICE_NAME': 'ai-travel-agent',
    'SERVER_URL': 'https://921c0e32e68a4652b6e3d6cca40beff2.apm.us-east-1.aws.cloud.es.io:443',  # Cambia <APM_SERVER_URL> por tu instancia Elastic APM
    'SECRET_TOKEN': 'QKUxauBYEwy4Fv3xwf',         # Cambia esto si utilizas un token
    'ENVIRONMENT': 'my-environment'                  # Cambia a 'production' si es necesario
}

# Inicializar APM
apm = ElasticAPM(app)

def populate_envs(sender_email, receiver_email, subject):
    os.environ['FROM_EMAIL'] = sender_email
    os.environ['TO_EMAIL'] = receiver_email
    os.environ['EMAIL_SUBJECT'] = subject

def send_email(sender_email, receiver_email, subject, thread_id):
    try:
        populate_envs(sender_email, receiver_email, subject)
        config = {'configurable': {'thread_id': thread_id}}
        st.session_state.agent.graph.invoke(None, config=config)
        st.success('Email sent successfully!')
        # Clear session state
        for key in ['travel_info', 'thread_id']:
            st.session_state.pop(key, None)
    except Exception as e:
        st.error(f'Error sending email: {e}')

def initialize_agent():
    if 'agent' not in st.session_state:
        st.session_state.agent = Agent()

def render_custom_css():
    st.markdown(
        '''
        <style>
        body {
            background-color: #f7f7f7;
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            color: #333;
        }
        .main-title {
            font-size: 3em;
            color: #1e1e1e;
            text-align: center;
            margin-bottom: 0.5em;
            font-weight: bold;
        }
        .sub-title {
            font-size: 1.3em;
            color: #666;
            text-align: left;
            margin-bottom: 0.5em;
        }
        .center-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 100%;
        }
        .query-box {
            width: 80%;
            max-width: 600px;
            margin-top: 0.5em;
            margin-bottom: 1em;
        }
        .query-container {
            width: 80%;
            max-width: 600px;
            margin: 0 auto;
        }
        .btn-primary {
            background-color: #0085ff;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            border: none;
            cursor: pointer;
        }
        .btn-primary:hover {
            background-color: #005f99;
        }
        .elastic-logo {
            width: 200px;
            margin-top: 20px;
        }
        .footer {
            font-size: 0.9em;
            color: #777;
            text-align: center;
            margin-top: 50px;
        }
        </style>
        ''', unsafe_allow_html=True)

def render_ui():
    st.markdown('<div class="center-container">', unsafe_allow_html=True)
    st.markdown('<div class="main-title">✈️🌍 AI Travel Agent 🏨🗺️</div>', unsafe_allow_html=True)
    st.markdown('<div class="query-container">', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Ingrese su consulta de viaje y obtenga información de vuelos y hoteles:</div>', unsafe_allow_html=True)
    user_input = st.text_area(
        'Travel Query',
        height=200,
        key='query',
        placeholder='Escriba aquí su consulta de viaje...',
    )
    st.markdown('</div>', unsafe_allow_html=True)

    
    return user_input

def process_query(user_input):
    if user_input:
        try:
            thread_id = str(uuid.uuid4())
            st.session_state.thread_id = thread_id

            messages = [HumanMessage(content=user_input)]
            config = {'configurable': {'thread_id': thread_id}}

            result = st.session_state.agent.graph.invoke({'messages': messages}, config=config)

            st.subheader('Lo que encontre para ti')
            st.write(result['messages'][-1].content)

            st.session_state.travel_info = result['messages'][-1].content

        except Exception as e:
            st.error(f'Error: {e}')
    else:
        st.error('Por favor ingrese una consulta de viaje.')

def render_email_form():
    send_email_option = st.radio('¿Quieres enviar esta información por correo electrónico?', ('No', 'Yes'))
    if send_email_option == 'Yes':
        with st.form(key='email_form'):
            sender_email = st.text_input('Sender Email')
            receiver_email = st.text_input('Receiver Email')
            subject = st.text_input('Email Subject', 'Travel Information')
            submit_button = st.form_submit_button(label='Send Email')

        if submit_button:
            if sender_email and receiver_email and subject:
                send_email(sender_email, receiver_email, subject, st.session_state.thread_id)
            else:
                st.error('Por favor complete todos los campos de correo electrónico.')

def main():
    initialize_agent()
    render_custom_css()
    user_input = render_ui()

    if st.button('Encuentralo'):
        process_query(user_input)

    if 'travel_info' in st.session_state:
        render_email_form()

    # Footer
    st.markdown('<div class="footer">Powered by Elastic APM</div>', unsafe_allow_html=True)

if __name__ == '__main__':
    main()