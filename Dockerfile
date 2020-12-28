FROM python:3

ENV PYTHONBUFFERED 1

WORKDIR /app

ADD . /app

COPY requirements.txt ./

RUN python3 -m pip install --upgrade https://storage.googleapis.com/tensorflow/mac/cpu/tensorflow-0.12.0-py3-none-any.whl

RUN pip install -r requirements.txt

COPY / ./

RUN python3 manage.py runserver 0.0.0.0:8000