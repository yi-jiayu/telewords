FROM python:3.7-alpine

RUN apk add --update --no-cache build-base

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "server.py" ]