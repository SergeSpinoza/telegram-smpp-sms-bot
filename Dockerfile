FROM python:3-alpine
LABEL maintainer="FEDONIN SERGE"

WORKDIR /app

COPY ./requirements.txt requirements.txt
# COPY ./settings.yaml settings.yaml
COPY ./smsbot.py smsbot.py

RUN apk add git && pip install -r requirements.txt

USER 1001

CMD [ "python", "./smsbot.py" ]

