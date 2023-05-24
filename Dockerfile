# syntax=docker/dockerfile:1

FROM python:3.10-slim-buster

RUN apt-get -y update
RUN apt-get -y upgrade
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ./src ./src
COPY ./db ./db
COPY ./bot.py ./bot.py
COPY ./.env ./.env


#WORKDIR /
#ENV FLASK_APP=app
#RUN chmod +x ./bot.py
CMD ["python", "./bot.py"]