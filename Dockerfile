FROM python:3.7-alpine

RUN apk add --update --no-cache build-base

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m nltk.downloader -d /usr/local/nltk_data wordnet

COPY . .

ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
