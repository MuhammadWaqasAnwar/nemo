FROM python:3.8

WORKDIR /usr/src/app

COPY requirements.txt .

RUN pip install -r requirements.txt

RUN apt-get update \
&& apt-get upgrade -y \
&& apt-get install -y \
&& apt-get -y install apt-utils gcc libpq-dev libsndfile-dev

COPY main.py .

COPY nvidiaTTS.py .

EXPOSE 5000

CMD python main.py
