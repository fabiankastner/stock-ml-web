FROM python:3

ENV PYTHONUNBUFFERED=1

RUN mkdir /app
WORKDIR /app

COPY ./requirements.txt /app/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN python3 -m pip install --upgrade https://storage.googleapis.com/tensorflow/mac/cpu/tensorflow-0.12.0-py3-none-any.whl

COPY ./stock-ml-web /app/