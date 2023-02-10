from fastapi import FastAPI, Query
import requests
import xml.etree.ElementTree as ET

app = FastAPI()

@app.get("/trends")
def get_trends(region: str = Query("US", max_length=2)):
    url = f"https://trends.google.com/trends/trendingsearches/daily/rss?geo={region}"
    response = requests.get(url)
    root = ET.fromstring(response.content)
    trends = []
    for item in root.iter("item"):
        title = item.find("title").text
        trends.append(title)
    return {"trends": trends}
