# syntax=docker/dockerfile:1
FROM python:3.10-slim
WORKDIR /RongWebApp
RUN apt-get update && apt-get install -y \
    nodejs npm libpq-dev gcc apache2 apache2-dev\
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . /RongWebApp/
RUN npm ci && npm run build
EXPOSE 8000
CMD [ "./launch.sh" ]