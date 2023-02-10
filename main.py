from fastapi import FastAPI, Query
import requests
import xml.etree.ElementTree as ET

from typing import List
from pydantic import BaseModel

class TrendResult(BaseModel):
    trends: List[str]

app = FastAPI()

@app.get("/api/trends", response_model=TrendResult)
def get_trends(region: str = Query("US", max_length=2)):
    url = f"https://trends.google.com/trends/trendingsearches/daily/rss?geo={region}"
    response = requests.get(url)
    root = ET.fromstring(response.content)
    trends = []
    for item in root.iter("item"):
        title = item.find("title").text
        trends.append(title)
    return {"trends": trends}
