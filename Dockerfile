FROM python:3.10-slim-bullseye

MAINTAINER LightQuantum

WORKDIR /app

RUN pip install --upgrade pip

COPY ./requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

COPY subscriber-backend ./subscriber-backend

CMD ["python", "-m", "subscriber-backend"]
