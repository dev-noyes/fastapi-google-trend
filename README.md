---
title: SideProject REST API
description: youtube rest api
author: Dongjun Yang
tags:
  - fastapi
  - python
  - chatgpt
  - cors
  - rest api
---

# 여러 REST API 를 배포해보았습니다.

## ✨ Features

- CORS 대응
- Google trend rest api
- Qrcode generator api
- Youtube reply api

## 문서

REST API 문서를 원하시는 분은 [문서](https://fastapi-google-trend.up.railway.app/redoc) 을 입력하시면 됩니다.

## Web Scaraping server

- saramin data
- inflearn data
- naver shopping data  

## Google Trend REST API template

Railway 의 fastapi 템플릿을 활용해서 만들었습니다.
ChatGPT 를 사용해서 google trends 를 나라별로 받아오는 api
region param 은 default 와 다른 나라들을 입력할 수 있게 되어있다.

### 사용법

- 미국데이터 : https://fastapi-google-trend.up.railway.app/api/trends
- 한국데이터 : https://fastapi-google-trend.up.railway.app/api/trends?region=KR
- 일본데이터 : https://fastapi-google-trend.up.railway.app/api/trends?region=JP

## Youtube reply api

유투브의 비디오 id 값을 입력하면 댓글과 대댓글을 알 수 있는 rest api.
video_id는 required param 이다.
JSON 의 구조가 복잡하기에 여러 key 값들에 대한 검증이 필요하지만 간단한 것만 해주었다.

### 사용법

- 사용하기 : https://fastapi-google-trend.up.railway.app/api/youtube_comments?url=IXwzT9fcEIQ

## Qrcode generator api

값을 입력하면 qrcode 를 base64 로 출력해주는 rest api 입니다.
query param name 은 required param 이다.
pillow 라이브러리도 함께 설치를 해줘야 qrcode 라이브러리가 사용가능하다.
없다면 pypng 설치가 필요하다.

### 사용법

- 사용하기 : https://fastapi-google-trend.up.railway.app/api/qrcode?name=1

## Color combination generator api

기본 5개의 Color 를 주는 rest api.
hex 값으로 데이터를 array 형식으로 뿌려줌.

### 사용법

- 사용하기 : https://fastapi-google-trend.up.railway.app/api/color
- 사용하기 : https://fastapi-google-trend.up.railway.app/api/color?n=5

## Youtube Hot video api

각 나라에 유명한 유투브 링크 제목 설명을 알려주는 API.
query param 으로 각 나라별로 유명한 유투브들을 알려준다.

### 사용법

- 사용하기 : https://fastapi-google-trend.up.railway.app/api/youtube_popular
- 사용하기 : https://fastapi-google-trend.up.railway.app/api/youtube_popular?region=KR

## Youtube info api

topic에 관련된 유투브 정보들을 조회순으로 알려준다.
구독자 수, 조회 수 대로 좋아진다. 최대 10개 보낸다.

- 사용하기 : https://fastapi-google-trend.up.railway.app/api/youtube_analysis?region=US&topic=USA

## Color Extracter

이미지를 업로드하면 이미지에 들어있는 메인 색깔들을 알려준다.
multipart 로 이미지를 업로드해야한다.
색깔의 개수는 query param 으로 정한다.

- 사용하기 : https://fastapi-google-trend.up.railway.app/api/color_palette
- 사용하기 : https://fastapi-google-trend.up.railway.app/api/color_palette?n=5
- 사용하기 : https://fastapi-google-trend.up.railway.app/api/color_palette?n=10

## Naver Blog Extracter

검색하고 싶은 검색어의 최신 약 200개의 네이버 블로그 아이디를 뽑아준다.
아이디는 서이추하기 편하게 블로그 주소로 출력된다.

- 사용하기 : https://fastapi-google-trend.up.railway.app/api/blogs?query=python

## Youtube live count

실시간 유튜브 구독자 확인 - 채널 id 무조건 입력해야한다.

- 사용하기 : https://fastapi-google-trend.up.railway.app/api/channel/{id}
