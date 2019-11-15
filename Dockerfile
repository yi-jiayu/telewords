FROM python:3.7-alpine

RUN apk add --update --no-cache build-base freetype-dev libpng-dev jpeg-dev ffmpeg

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "server.py" ]