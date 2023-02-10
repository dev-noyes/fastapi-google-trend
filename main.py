from fastapi import FastAPI, Query
import requests
import xml.etree.ElementTree as ET
from fastapi.middleware.cors import CORSMiddleware

from typing import List
from pydantic import BaseModel


class TrendResult(BaseModel):
    trends: List[str]


app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
