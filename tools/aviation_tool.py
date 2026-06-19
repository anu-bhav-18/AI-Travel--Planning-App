import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

AVIATION_API_KEY = os.getenv("AVIATIONSTACK_API_KEY")
BASE_URL = "http://api.aviationstack.com/v1/flights"

def search_flight():
    params = {
        "access_key":AVIATION_API_KEY,
        "limit":10
    }
    response = requests.get(BASE_URL,params=params)
    data = response.json()
    flights =[]
    if "data" in data:
        for flight in data["data"]:
            airline_name = flight["airline"].get("name","Unknow")
            departure_place = flight['departure'].get('airport',"Unknow")
            arrival_place = flight['arrival'].get('airport',"Unknow")
            status = flight['flight_status']
            flights.append(f"""
            Airline Name :-{airline_name}
            Departure Airport:-{departure_place}
            Arrival Airport :-{arrival_place}
            Status :- {status}
            """)
        
    return "/n".join(flights)

   


