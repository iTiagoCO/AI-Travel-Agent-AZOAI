import os
from typing import Optional
from pydantic import BaseModel, Field
from serpapi import GoogleSearch
from langchain_core.tools import tool
from elasticapm import capture_span

class HotelsInput(BaseModel):
    q: str = Field(description="Location of the hotel (e.g., 'Amsterdam').")
    check_in_date: str = Field(description="Check-in date in YYYY-MM-DD format (e.g., 2024-12-01).")
    check_out_date: str = Field(description="Check-out date in YYYY-MM-DD format (e.g., 2024-12-02).")
    adults: Optional[int] = Field(default=1, description="Number of adults. Default is 1.")
    children: Optional[int] = Field(default=0, description="Number of children. Default is 0.")
    rooms: Optional[int] = Field(default=1, description="Number of rooms. Default is 1.")


class HotelsInputSchema(BaseModel):
    params: HotelsInput


@tool(args_schema=HotelsInputSchema)
def hotels_finder(params: HotelsInput):
    """
    Find hotels using the Google Hotels engine with the provided parameters.

    Args:
        params (HotelsInput): Search parameters for finding hotels.

    Returns:
        list | str: Top 5 hotels or an error message.
    """
    # Construct search parameters
    search_params = {
        "api_key": os.environ.get("SERPAPI_API_KEY"),
        "engine": "google_hotels",
        "q": params.q,
        "check_in_date": params.check_in_date,
        "check_out_date": params.check_out_date,
        "currency": "USD",
        "adults": params.adults or 1,
        "children": params.children or 0,
        "rooms": params.rooms or 1
    }

    try:
        # Debugging: Print the search parameters
        print("Debug: Search Params ->", search_params)

        # Check if API key is set
        if not search_params["api_key"]:
            raise ValueError("API key is missing. Set it in the SERPAPI_API_KEY environment variable.")

        # Perform the search
        search = GoogleSearch(search_params)
        results = search.get_dict()

        # Debugging: Print the raw results
        print("Debug: Raw Results ->", results)

        # Check if properties exist in results
        if not results.get("properties"):
            return "No hotels found for the given criteria. Try adjusting your search parameters."

        # Return top 5 hotels
        return results.get("properties", [])[:5]

    except Exception as e:
        # Catch and return errors for debugging
        print(f"Error: {str(e)}")
        capture_span("flights_finder_error", "error")
        return f"Error during hotel search: {str(e)}"
