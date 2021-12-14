FROM python:3.8-slim AS base
RUN apt-get update && apt-get install --no-install-recommends --yes python3

RUN pip install pika
RUN pip install -U requests

COPY ./traductor.py ./traductor.py

CMD ["python", "traductor.py"]