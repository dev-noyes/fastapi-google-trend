FROM python:latest
MAINTAINER DongjunYang 

WORKDIR /app/

COPY ./main.py /app/
COPY ./requirements.txt /app/

ARG PORT 8000

RUN pip install -r requirements.txt
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 -y

CMD uvicorn --host=0.0.0.0 --port $PORT main:app
