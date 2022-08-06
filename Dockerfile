FROM python:3.8.5

COPY . /HomeDrive

WORKDIR /HomeDrive

RUN apt update && apt -y install default-libmysqlclient-dev
RUN pip3 install -r requirements.txt

CMD gunicorn -c gunicorn.conf.py app:app --preload