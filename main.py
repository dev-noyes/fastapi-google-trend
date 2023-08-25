from fastapi import FastAPI, Query, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

import datetime
import requests
import xml.etree.ElementTree as ET
from cv2 import dnn_superres
from dotenv import load_dotenv

import qrcode
import base64
import os
from random import choice

from PIL import Image
import numpy as np
import colorgram
import io

import urllib.request
import json
from random import randint
from datetime import date

load_dotenv()
GCP_YT_APIKEY = os.environ.get('GCP_YT_APIKEY')
NAVER_API_ID = os.environ.get('NAVER_API_ID')
NAVER_API_PW = os.environ.get('NAVER_API_PW')

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


@app.get("/")
async def root():
    return {"message": "Hello World"}


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
    try:
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
    except Exception as e:
        return {"result": "Error@Failed to process."}


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
        'order': "viewCount",
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


@app.post("/api/color_palette", response_model=ExtractData)
async def color_palette(n: int = 10, file: UploadFile = File(...)):
    """
    Get the colors from the image upload with multipart `file`.

    - `file`: image file multi part

    Returns the retrieved item.
    """
    # Convert the file to a NumPy array
    contents = await file.read()
    img = Image.open(io.BytesIO(contents))

    # Extract colors using colorgram library
    colors = colorgram.extract(img, n)

    # Get hex values of the colors
    color_palette = [
        f"#{c.rgb.r:02x}{c.rgb.g:02x}{c.rgb.b:02x}" for c in colors]

    return {"color_palette": color_palette, "num_colors": n}


def get_search(query, start):
    list_ids = []
    query = urllib.parse.quote(query)
    url = f"https://openapi.naver.com/v1/search/blog?query={query}&sort=date&display=100&start={start}"
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", NAVER_API_ID)
    request.add_header("X-Naver-Client-Secret", NAVER_API_PW)
    response = urllib.request.urlopen(request)
    rescode = response.getcode()
    if (rescode == 200):
        response_body = response.read()
        body = response_body.decode('utf-8')
        data = json.loads(body)
        for item in data["items"]:
            id = item["bloggerlink"].split("blog.naver.com/")
            if (len(id) > 1):
                list_ids.append(
                    f"https://m.blog.naver.com/PostList.nhn?blogId={id[1]}")
    else:
        print("Error Code:" + rescode)

    return list_ids


@app.get("/api/blogs", response_model=list[str])
async def blog_data(query: str = Query(..., required=True)):
    """
    Get the latest blog url with query param `query`.

    - `query`: An optional query parameter to search for specific region trend.

    Returns the retrieved item.
    """
    data1 = get_search(query, 1)
    data2 = get_search(query, 101)
    data1.extend(data2)
    blogs = list(dict.fromkeys(data1))
    return blogs


class SubscriberData(BaseModel):
    subscriber_count: int


@app.get("/api/channel/{channel_id}", response_model=SubscriberData)
async def subscribers(channel_id: str):
    """
    Get the live subscriber count with path `channel_id`.

    - `channel_id`: An required path parameter for youtube channel

    Returns the retrieved item.
    """
    url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={channel_id}&key={GCP_YT_APIKEY}"

    response = requests.get(url)
    data = response.json()

    if "items" in data:
        subscriber_count = data["items"][0]["statistics"]["subscriberCount"]
    else:
        subscriber_count = 0

    return {"subscriber_count": subscriber_count}


@app.get("/search/inflearn")
async def search(q: str | None = None):
    """_summary_
    get the data from inflearn

    Args:
        q (str | None, optional): _description_. Defaults to None.

    Raises:
        HTTPException: _description_

    Returns:
        array: data array
    """
    if q is None:
        raise HTTPException(status_code=404, detail="Item not found")

    query = q
    encoded_query = urllib.parse.quote(query)
    url = f'https://www.inflearn.com/courses?s={encoded_query}'

    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(response.content, 'html.parser')
    arr = []
    for course in soup.find_all('div', {'class': 'course_card_item'}):
        fxd_data = course.find('div', {'class': 'course-data'})['fxd-data']
        course_data = json.loads(fxd_data)
        course_data["course_title"] = str(
            course_data["course_title"]).replace(",", "")
        course_data["first_category"] = str(
            course_data["first_category"]).replace(",", "")
        course_data["second_category"] = str(
            course_data["second_category"]).replace(",", "")
        course_data["seq0_instructor_name"] = str(
            course_data["seq0_instructor_name"]).replace(",", "")
        course_data["skill_tag"] = str(
            course_data["skill_tag"]).replace(",", "")
        course_data["discount_title"] = str(
            course_data["discount_title"]).replace(",", "", 2)
        if (course_data["discount_id"] == None):
            course_data["discount_id"] = "None"
        if (course_data["discount_rate"] == None):
            course_data["discount_rate"] = 0
        if (course_data["installment_price"] == None):
            course_data["installment_price"] = "None"
        if (course_data["installment_month"] == None):
            course_data["installment_month"] = "None"
        arr.append(course_data)
    return (arr)


@app.get("/search/saramin")
async def search(q: str | None = None, page: int = 1, limit: int = 40):
    """_summary_
    get the data from saramin

    Args:
        q (str | None, optional): _description_. Defaults to None.
        page (int, optional): _description_. Defaults to 1.
        limit (int, optional): _description_. Defaults to 40.

    Raises:
        HTTPException: _description_

    Returns:
        _type_: _description_
    """
    if q is None:
        raise HTTPException(status_code=404, detail="Item not found")
    query = q
    encoded_query = urllib.parse.quote(query)
    raw = requests.get(
        f'https://www.saramin.co.kr/zf_user/search?search_area=main&search_done=y&search_optional_item=n&searchType=recently&recruitSort=reg_dt&recruitPage={page}&searchword={encoded_query}&recruitPageCount={limit}', headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(raw.text, "html.parser")
    results = soup.select("div.item_recruit")
    arr = []
    for ar in results:
        obj = {}
        title = ar.select_one("a")['title']
        title = title.replace(",", "")
        obj["title"] = title

        link = ar.select_one("a")['href']
        obj["link"] = f"https://www.saramin.co.kr{link}"

        company = ar.select_one(
            'div.area_corp > strong > a').text.strip()
        obj["company"] = company

        companylink = ar.select_one(
            'div.area_corp > strong > a')['href']
        obj["companylink"] = f"https://www.saramin.co.kr{companylink}"

        enddate = ar.select_one('div.job_date > span').text.strip()
        obj["enddate"] = enddate

        infos = ar.select('div.job_condition > span')
        for idx in range(len(infos)):
            if (idx == 0):
                obj["location"] = infos[idx].text.strip()
            if (idx == 1):
                obj["type"] = infos[idx].text.strip()
            if (idx == 2):
                obj["school"] = infos[idx].text.strip()
            if (idx == 3):
                obj["jobtype"] = infos[idx].text.strip()

        tags = ar.select('div.job_sector > b > a')
        tag_vip = ""
        for tag in tags:
            tag_vip += f"#{tag.text.strip()} "
        obj["tag_vip"] = tag_vip

        tags = ar.select('div.job_sector > a')
        tag_normal = ""
        for tag in tags:
            tag_normal += f"#{tag.text.strip()} "
        obj["tag_normal"] = tag_normal

        registerdate = ar.select_one('div.job_sector > span').text.strip()
        obj["registerdate"] = registerdate.replace(
            "등록일", "").replace("수정일", "")

        now = datetime.datetime.now()
        nowDate = now.strftime('%Y-%m-%d')
        obj["date"] = nowDate

        try:
            apply = ar.select_one("button.sri_btn_xs").text
        except:
            apply = "홈페이지지원"
        obj["apply"] = apply
        arr.append(obj)
    return arr