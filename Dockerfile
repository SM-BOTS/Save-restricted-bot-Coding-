# DONT REMOVE CREDITS
# Developer: [ Eva Rose ] (https://t.me/EvaRoseX)
# Join TG Channel: https://t.me/ERBotsUpdate
# Ask Doubt On Telegram: @EvaRoseX
# DEVELOPER: BY EVA ROSE


FROM python:3.10.8-slim-buster
WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD gunicorn app:app & python3 bot.py
