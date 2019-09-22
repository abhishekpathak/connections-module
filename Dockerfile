FROM python:3.7.4-buster

MAINTAINER Abhishek Pathak "4abhishekpathak@gmail.com"

COPY . /app

WORKDIR /app/server

RUN ["pip3", "install", "pipenv"]

RUN ["pipenv", "install"]

#ENV FLASK_APP server/app.py

CMD pipenv run flask run --host='0.0.0.0'


