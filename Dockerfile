FROM python:3.8.5

COPY . /HomeDrive

WORKDIR /HomeDrive

RUN pip3 install -r requirements.txt

CMD ["python3", "app.py"]