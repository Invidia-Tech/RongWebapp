# syntax=docker/dockerfile:1
FROM node:slim
WORKDIR /RongWebApp
RUN apt-get update && apt-get install -y \
    python3 \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt requirements.txt
RUN npm ci && npm run build && pip install -r requirements.txt
COPY . .
CMD [ "./migrate_and_update.sh" ]