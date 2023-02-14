from fastapi import FastAPI, Query

from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import requests
import xml.etree.ElementTree as ET
# import re
from dotenv import load_dotenv

import qrcode
import base64
from io import BytesIO
import os
from random import choice


load_dotenv()
GCP_YT_APIKEY = os.environ.get('GCP_YT_APIKEY')

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


class TrendResult(BaseModel):
    trends: list[str] = []


@app.get("/api/trends", response_model=TrendResult)
async def get_trends(region: str = Query("US", max_length=2)):
    url = f"https://trends.google.com/trends/trendingsearches/daily/rss?geo={region}"
    response = requests.get(url)
    root = ET.fromstring(response.content)
    trends = []
    for item in root.iter("item"):
        title = item.find("title").text
        trends.append(title)
    return {"trends": trends}


class ReplyResult(BaseModel):
    comment: str
    replies: list[str] = []


@app.get("/api/youtube_comments", response_model=list[ReplyResult])
async def youtube_comments(url: str = Query(..., required=True)):
    # video_id = re.search(r"v=([^&]+)", url).group(1)
    video_id = url

    # Get the comments from the YouTube API
    api_key = GCP_YT_APIKEY
    api_url = f"https://www.googleapis.com/youtube/v3/commentThreads?part=snippet,replies&videoId={video_id}&textFormat=plainText&maxResults=100&order=time&key={api_key}"
    response = requests.get(api_url)
    comments = response.json()

    # Extract the comments and replies from the API response
    results = []
    for comment in comments["items"]:
        comment_text = {}
        reply_text = []
        # check json key value
        if "snippet" in comment:
            comment_text = comment["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
        # check json key value
        if "replies" in comment:
            replies = [reply["snippet"]["textDisplay"]
                       for reply in comment["replies"]["comments"]]
            reply_text = replies
        results += [{"comment": comment_text, "replies": reply_text}]

    return results


class QrcodeResult(BaseModel):
    result: str


@app.get("/api/qrcode", response_model=QrcodeResult)
async def qrcode_generator(name: str = Query(..., min_length=1, max_length=30, required=True)):
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4
    )
    qr.add_data(name)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return {"result": base64.b64encode(buffer.getvalue()).decode("utf-8")}


class ColorResult(BaseModel):
    result: list[str] = []


@app.get("/api/color", response_model=ColorResult)
async def generate_color_combination(n: int = 5):
    # Define a list of all possible HEX color codes
    colors = [f"#{format(i, '06x')}" for i in range(16777216)]
    color_combination = [choice(colors) for i in range(n)]
    return {"result": color_combination}


class PopularResult(BaseModel):
    link: str
    title: str
    description: str | None = None
    nation: str


@app.get("/api/youtube_popular", response_model=list[PopularResult])
async def get_popular_videos(nation: str = "US"):
    api_key = GCP_YT_APIKEY
    response = requests.get("https://www.googleapis.com/youtube/v3/videos",
                            params={"part": "snippet", "chart": "mostPopular", "regionCode": nation,
                                    "key": api_key})
    items = response.json()["items"]
    videos = [{"link": f"https://www.youtube.com/watch?v={item['id']}",
               "title": item["snippet"]["title"],
               "description": item["snippet"]["description"],
               "nation": nation} for item in items]
    return videos
