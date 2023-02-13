---
title: SideProject REST API
description: sample rest api
author: Dongjun Yang
tags:
  - fastapi
  - python
  - chatgpt
  - cors
---

# 여러 REST API 를 배포해보았습니다.

## ✨ Features

- CORS 대응
- Google trend rest api 
- Qrcode generator api
- youtube reply api

## 문서

REST API 문서를 원하시는 분은 [문서](https://fastapi-google-trend.up.railway.app/redoc) 을 입력하시면 됩니다.


## Google Trend REST API template

Railway 의 fastapi 템플릿을 활용해서 만들었습니다. 
ChatGPT 를 사용해서 google trends 를 나라별로 받아오는 api를 만들었습니다.

### 사용법 

- 미국데이터 : https://fastapi-google-trend.up.railway.app/api/trends 
- 한국데이터 : https://fastapi-google-trend.up.railway.app/api/trends?region=KR
- 일본데이터 : https://fastapi-google-trend.up.railway.app/api/trends?region=JP

## Youtube reply api

유투브의 비디오 id 값을 입력하면 댓글과 대댓글을 알 수 있는 rest api.

### 사용법 

- 사용하기 : https://fastapi-google-trend.up.railway.app/api/youtube_comments?url=IXwzT9fcEIQ

## Qrcode generator api

값을 입력하면 qrcode 를 base64 로 출력해주는 rest api 입니다.

### 사용법 

- 사용하기 : https://fastapi-google-trend.up.railway.app/api/qrcode?name=1

