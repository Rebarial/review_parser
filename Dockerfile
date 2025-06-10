FROM python:3.10-slim-buster

RUN sudo apt update && sudo apt upgrade -y

RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

RUN sudo apt-get install -f

RUN dpkg -i google-chrome-stable_current_amd64.deb

RUN apt install python3-pip

RUN pip3 install selenium webdriver-manager

WORKDIR /code/review_parser

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /code/review_parser/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /code/