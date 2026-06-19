import os
from typing import Annotated,TypedDict
import psycopg
import operator
from langgraph.graph import START , END, StateGraph
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_core.messages import (
    AnyMessage,
    HumanMessage,
    AIMessage,
    SystemMessage
)
from langchain_groq import ChatGroq
from tools.aviation_tool import search_flight
from tools.tavily_tool import search_hotels
from dotenv import load_dotenv

load_dotenv()

LLM_API_KEY = os.getenv("GROQ_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

llm = ChatGroq(model="llama-3.3-70b-versatile")

class STATE(TypedDict):
    messages:Annotated[list[AnyMessage],operator.add]
    user_query:str
    hotel_result:str
    flight_result:str
    itinerrarry :str
    llm_call:int

#hotel agent
def flight_Agent(state:STATE):
    user_query = state['user_query']
    flight_data = search_flight()
    result = {
        'flight_result':flight_data,
        'messages':[AIMessage(content="flight data feached.")],
        'llm_call':state['llm_call'] + 1
    }
    return result

#hotel agent
def hotel_agent(state:STATE):
    user_query = state['user_query']
    hotel_result = search_hotels(user_query)
    result = {
        'hotel_result':hotel_result,
        'messages':[AIMessage(content="featched hotel data.")],
        'llm_call':state['llm_call'] +1
    }
    return result

def itinerrarry_agent(state:STATE):
    prompt =f"""
    Create a travel itinerray.
    user qury : {state['user_query']}
    flights data : {state['flight_result']}
    hotel data : {state['hotel_result']} 
    """
    response = llm.invoke(
        [
            SystemMessage(content="You are an expert travel planner"),
            HumanMessage(content=prompt)
        ]
    )
    result = {
        'itinerrarry':response.content,
        'messages':[response],
        'llm_call':state['llm_call']+1
    }
    return result

def main_agent(state:STATE):
    prompt =f"""
    Generate a final response for travel.
    user query :-{state["user_query"]}
    flight result :-{state['flight_result']}
    hotel result :- {state['hotel_result']}
    itinerrarry : -{state["itinerrarry"]}

    """

    response = llm.invoke(
        [
            HumanMessage(content=prompt)
        ]
    )
    return {
        "messages":[response],
        "llm_call":state['llm_call']+1
    }



graph_builder = StateGraph(STATE)
#nodes
graph_builder.add_node("flight_agent",flight_Agent)
graph_builder.add_node("hotel_agent",hotel_agent)
graph_builder.add_node("itinearry_agent",itinerrarry_agent)
graph_builder.add_node("main_agent",main_agent)

#edges
graph_builder.add_edge(START,"flight_agent")
graph_builder.add_edge("flight_agent","hotel_agent")
graph_builder.add_edge("hotel_agent","itinearry_agent")
graph_builder.add_edge("itinearry_agent","main_agent")
graph_builder.add_edge("main_agent",END)

#_conn = psycopg.connect(DATABASE_URL)
#checkpointer = PostgresSaver(_conn)
#checkpointer.setup()

app = graph_builder.compile()

if __name__=="__main__":
    config ={
        "configurable":{
            "thread_id":"user_anubhav"
        }
    }
    user_input = input("Enter your prompt:-")
    response = app.invoke({
        "messages":[
            HumanMessage(content=user_input)
            ],
        "user_query":user_input,
        'flight_result':" ",
        'hotel_result':" ",
        'itinerrarry':" ",
        "llm_call":0
        },
        config = config
    )
    print(f"\n FINAL RESPONSE:-\n")
    for msg in response['messages']:
        print(msg.content)


    


