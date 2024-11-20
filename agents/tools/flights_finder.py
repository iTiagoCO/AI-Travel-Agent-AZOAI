import os
from typing import Optional

# from pydantic import BaseModel, Field
import serpapi
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from serpapi.google_search import GoogleSearch
from elasticapm import capture_span




class FlightsInput(BaseModel):
    departure_airport: Optional[str] = Field(description='Departure airport code (IATA)')
    arrival_airport: Optional[str] = Field(description='Arrival airport code (IATA)')
    outbound_date: Optional[str] = Field(description='Parameter defines the outbound date. The format is YYYY-MM-DD. e.g. 2024-06-22')
    return_date: Optional[str] = Field(description='Parameter defines the return date. The format is YYYY-MM-DD. e.g. 2024-06-28')
    adults: Optional[int] = Field(1, description='Parameter defines the number of adults. Default to 1.')
    children: Optional[int] = Field(0, description='Parameter defines the number of children. Default to 0.')
    infants_in_seat: Optional[int] = Field(0, description='Parameter defines the number of infants in seat. Default to 0.')
    infants_on_lap: Optional[int] = Field(0, description='Parameter defines the number of infants on lap. Default to 0.')


class FlightsInputSchema(BaseModel):
    params: FlightsInput


@tool(args_schema=FlightsInputSchema)
@capture_span("flights_search")  # Inicia una transacción APM para la búsqueda de vuelos
def flights_finder(params: FlightsInput):
    """
    Find flights using the Google Flights engine.

    Returns:
        dict: Flight search results.
    """
    search_params = {
        'api_key': os.environ.get('SERPAPI_API_KEY'),
        'engine': 'google_flights',
        'hl': 'en',
        'gl': 'us',
        'departure_id': params.departure_airport,
        'arrival_id': params.arrival_airport,
        'outbound_date': params.outbound_date,
        'return_date': params.return_date,
        'currency': 'USD',
        'adults': params.adults,
        'infants_in_seat': params.infants_in_seat,
        'stops': '1',
        'infants_on_lap': params.infants_on_lap,
        'children': params.children
    }

    try:
        search = GoogleSearch(search_params)
        results = search.get_dict()
        return results.get('best_flights', 'No flights found.')
    except Exception as e:
        capture_span("flights_finder_error", "error")
        return f"Error during flight search: {str(e)}"
