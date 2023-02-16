from fastapi import FastAPI, Query

from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

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

app = FastAPI(
    docs_url="/docs",
    redoc_url="/redoc",
    title="Noyes's REST API",
    description="This api is written by yangdongjun and it is open-sourced. The making films are on youtube.",
    version="0.2.0",
    openapi_url="/openapi.json",
)

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
async def google_trends(region: str = Query("US", max_length=2)):
    """
    Get the latest google trend every country with query param `region`.

    - `region`: An optional query parameter to search for specific region trend. default : US

    Returns the retrieved item.
    """
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
    """
    Get the comment and replies of youtube video with query param `url`.

    - `url`: An required query parameter to specific videio id of youtube.

    Returns the retrieved item.
    """
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
    """
    Get the base64 result with query param `name`.

    - `name`: An required query parameter to get the result of base64 qrcode.

    Returns the retrieved item.
    """
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
async def color_combination(n: int = 5):
    """
    Define a list of all possible HEX color codes with query param `n`.

    - `n`: Number of color combination. If n is 5, the api should give 5 results.

    Returns the retrieved item.
    """
    # Define a list of all possible HEX color codes
    # 16777216 is too slow
    # colors = [f"#{format(i, '06x')}" for i in range(16777216)]
    colors = ["#000000", "#000080", "#0000ff", "#008000", "#008080", "#00ff00", "#00ffff", "#800000",
              "#800080", "#808000", "#808080", "#c0c0c0", "#ff0000", "#ff00ff", "#ffff00", "#ffffff",
              "#7f0000", "#7f007f", "#7f00ff", "#007f00", "#007f7f", "#00ff7f", "#00ff7f", "#7f3f00",
              "#7f007f", "#7f7f00", "#7f7f7f", "#ff7f7f", "#ff7fff", "#ffff7f", "#4d4d4d", "#0000c6",
              "#0000ff", "#00c600", "#00c6c6", "#00ff00", "#00ffff", "#c60000", "#c600c6", "#c6c600",
              "#c6c6c6", "#ff0000", "#ff00ff", "#ffff00", "#ffffff", "#c10000", "#c100c1", "#c1c100",
              "#c1c1c1", "#ff7f7f", "#ff7fff", "#ffff7f", "#7f7f7f", "#1e1e1e", "#1e1e9c", "#1e9c1e",
              "#1e9c9c", "#9c1e1e", "#9c1e9c", "#9c9c1e", "#9c9c9c", "#4c4c4c", "#4c4cff", "#4cff4c",
              "#4cff4c", "#4cffcf", "#4cffff", "#ff4c4c", "#ff4cff", "#ffff4c", "#ffff4c", "#ff4ccf",
              "#ff4fff", "#ff7f00", "#ff7fff", "#ffaa00", "#ffffaa", "#cf9f9f", "#e6e6e6", "#b5b5b5",
              "#939393", "#4c4cff", "#4cff4c", "#4cffff", "#4c4c4c", "#ff4c4c", "#ff4cff", "#ffff4c",
              "#ffff4c", "#ff4ccf", "#ff4fff", "#ff7f00", "#ff7fff", "#ffaa00", "#ffffaa", "#cf9f9f",
              "#e6e6e6", "#b5b5b5", "#939393", "#7f7f00", "#7f7f7f", "#7f7fff", "#7fff00", "#7fff7f"
              ]
    color_combination = [choice(colors) for i in range(n)]
    return {"result": color_combination}


class PopularResult(BaseModel):
    link: str
    title: str
    description: str | None = None
    region: str


@app.get("/api/youtube_popular", response_model=list[PopularResult])
async def youtube_popular_videos(region: str = Query("US", max_length=2)):
    """
    Get the popular youtube video info with query param `region`.

    - `region`: An optional query parameter to search for specific region youtube. default : US

    Returns the retrieved item.
    """
    api_key = GCP_YT_APIKEY
    response = requests.get("https://www.googleapis.com/youtube/v3/videos",
                            params={"part": "snippet", "chart": "mostPopular", "regionCode": region,
                                    "key": api_key})
    items = response.json()["items"]
    videos = [{"link": f"https://www.youtube.com/watch?v={item['id']}",
               "title": item["snippet"]["title"],
               "description": item["snippet"]["description"],
               "region": region} for item in items]
    return videos
