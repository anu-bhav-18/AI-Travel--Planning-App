import os
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()
TAVILY_API_KEY = os.getenv("TRAVILY_API_KEY")
client = TavilyClient(api_key = TAVILY_API_KEY)

#testing the client first
#response = client.search(query="best hotel in patna")
#print(response)

def search_hotels(query):
    response = client.search(query,max_result =10)
    hotets =[]
    for i , hotel in enumerate(response['results'],1):
        url= hotel['url']
        title = hotel['title']
        content = hotel['content']
        hotets.append(f"""
        index:-{i}
        url :- {url}
        title:-{title}
        content:-{content}
        """)
    return "\n".join(hotets)