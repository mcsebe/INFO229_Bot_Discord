FROM python:3.8-slim AS base
RUN apt-get update && apt-get install --no-install-recommends --yes python3

RUN pip install pika
RUN pip install -U spotipy

COPY ./spotify.py ./spotify.py

CMD ["python", "spotify.py"]