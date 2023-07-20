FROM python:3.11-slim

WORKDIR /app

COPY requirements*.txt /app

RUN pip3 install -r requirements-dev.txt

COPY ./src /app

CMD ["python3", "-m", "app"]