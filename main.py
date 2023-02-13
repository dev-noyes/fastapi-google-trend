from fastapi import FastAPI, Query

from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

import requests
import xml.etree.ElementTree as ET
# import re
import qrcode
import base64
from io import BytesIO
from dotenv import load_dotenv
import os

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
    class Config:
        orm_mode = True


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


class ReplyResult(BaseModel):
    comment: str
    replies: list[str] = []
    class Config:
        orm_mode = True


@app.get("/api/youtube_comments", response_model=list[ReplyResult])
async def youtube_comments(url: str = Query(..., required=True)):
    # video_id = re.search(r"v=([^&]+)", url).group(1)
    video_id = url

    # Get the comments from the YouTube API
    api_key = GCP_YT_APIKEY
    api_url = f"https://www.googleapis.com/youtube/v3/commentThreads?part=snippet,replies&videoId={video_id}&textFormat=plainText&&maxResults=100&order=time&key={api_key}"
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
async def qrcode_generator(name: str = Query(..., min_length=1, max_length=30)):
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
