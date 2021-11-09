FROM python:3.8

COPY requirements-test.txt /tmp/
RUN pip install -r /tmp/requirements-test.txt

COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

WORKDIR /app
ADD . /app
