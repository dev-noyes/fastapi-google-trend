from fastapi import FastAPI, Query, File, UploadFile

from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional

import requests
import xml.etree.ElementTree as ET
# import re
from dotenv import load_dotenv

import qrcode
import base64
from io import BytesIO
import os
from random import choice

from PIL import Image
import numpy as np
import colorgram
import io


load_dotenv()
GCP_YT_APIKEY = os.environ.get('GCP_YT_APIKEY')

app = FastAPI(
    docs_url="/docs",
    redoc_url="/redoc",
    title="Noyes's REST API",
    description="This api is written by yangdongjun and it is open-sourced. The making films are on youtube.",
    version="0.3.0",
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

# Define a Pydantic model for the YouTube video data


class VideoData(BaseModel):
    title: str
    view_count: int
    subscribers: int
    channel_title: str
    link: str

# Define a function to retrieve the YouTube video data


def get_video_data(topic: str, region: str) -> Optional[VideoData]:
    # Construct the URL for the video search endpoint
    search_url = 'https://www.googleapis.com/youtube/v3/search'
    search_params = {
        'q': topic,
        'type': 'video',
        'regionCode': region,
        'part': 'id',
        'maxResults': 10,
        'order':"viewCount",
        'key': GCP_YT_APIKEY
    }

    videos = []

    # Call the video search endpoint to get the next page of results
    search_response = requests.get(search_url, params=search_params)
    search_response.raise_for_status()
    search_data = search_response.json()

    # Extract the video IDs from the search results
    video_ids = [item['id']['videoId'] for item in search_data['items']]

    # Construct the URL for the video details endpoint
    details_url = 'https://www.googleapis.com/youtube/v3/videos'
    details_params = {
        'id': ','.join(video_ids),
        'part': 'snippet,statistics',
        'key': GCP_YT_APIKEY
    }

    # Call the video details endpoint to get the video data
    details_response = requests.get(details_url, params=details_params)
    details_response.raise_for_status()
    details_data = details_response.json()

    # Extract the relevant data from the video details response
    for item in details_data['items']:
        snippet = item['snippet']
        statistics = item['statistics']
        title = snippet['title']
        view_count = int(statistics['viewCount'])
        channel_title = snippet['channelTitle']
        link = f"https://www.youtube.com/watch?v={item['id']}"

        # Get the channel ID for this video
        channel_id = snippet['channelId']

        # Construct the URL for the channel details endpoint
        channels_url = 'https://www.googleapis.com/youtube/v3/channels'
        channels_params = {
            'id': channel_id,
            'part': 'statistics',
            'key': GCP_YT_APIKEY
        }

        # Call the channel details endpoint to get the subscriber count
        channels_response = requests.get(
            channels_url, params=channels_params)
        channels_response.raise_for_status()
        channels_data = channels_response.json()

        # Extract the subscriber count from the channel details response
        subscribers = int(
            channels_data['items'][0]['statistics'].get('subscriberCount', 0))

        videos.append(VideoData(
            title=title,
            link=link,
            view_count=view_count,
            channel_title=channel_title,
            subscribers=subscribers
        ))

    return videos

# Define the API endpoint


@app.get('/api/youtube_analysis', response_model=list[VideoData])
async def youtube_data(
    topic: str = Query(..., description='The topic to search for'),
    region: str = Query(...,
                        description='The region to search in (ISO 3166-1 alpha-2 code)')
) -> Optional[VideoData]:
    # Call the get_video_data function and return the result
    return get_video_data(topic, region)


class ExtractData(BaseModel):
    color_palette: list[str] = []
    num_colors: int

@app.post("/api/color_palette")
async def color_palette(n: int = 10, file: UploadFile = File(...)):
    # Convert the file to a NumPy array
    contents = await file.read()
    img = Image.open(io.BytesIO(contents))

    # Extract colors using colorgram library
    colors = colorgram.extract(img, n)

    # Get hex values of the colors
    color_palette = [
        f"#{c.rgb.r:02x}{c.rgb.g:02x}{c.rgb.b:02x}" for c in colors]

    return {"color_palette": color_palette, "num_colors":n}
