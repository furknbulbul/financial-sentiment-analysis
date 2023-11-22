
import pandas as pd
import requests


API_KEY = "784462b2-f5e2-43c7-b3cf-f41b613e4122"

DATE = "2023-01-01"



info = []
def json(url):
    response=requests.get(url)
    if response.status_code == 200:  #It checks if the response status code is equal to 200, which indicates a successful response (status code 200 means "OK").
        x=response.json()  #If the response is successful, it extracts the JSON data from the response using response.json().
        info.append(x)
    else:
        return False
    return True

def retrieve_info(marcet):
    pages = 1 
    while True:
        url = f"https://content.guardianapis.com/search?q={marcet}&from-date={DATE}&api-key={API_KEY}&page={pages}"
        if not json(url):    
            break
        pages += 1 
        
    return pages, info

def parse_info(info, pages):
    finallist=[]
    try:
        for k in range(0,pages):
            for j in range(0,10):
                value=dict(typee=info[k]['response']['results'][j]['type'],
                        sectionId=info[k]['response']['results'][j]['sectionId'],
                        sectionName=info[k]['response']['results'][j]['sectionName'],
                        webtitle=info[k]['response']['results'][j]['webTitle'],
                        publisheddate=info[k]['response']['results'][j]['webPublicationDate'],
            )
                finallist.append(value)
    except IndexError:
        print("done")

    datanew=pd.DataFrame(finallist)
    return datanew
