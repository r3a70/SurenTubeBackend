FROM python:3.11-alpine

ARG USERNAME=youtube-downloader
ARG USER_UID=1000

RUN apk update && apk add build-base && \
    adduser -g ${USERNAME} ${USERNAME} --disabled-password --uid ${USER_UID} 

USER $USERNAME

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt
