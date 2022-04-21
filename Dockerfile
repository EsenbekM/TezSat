FROM python:3.8

RUN set -ex && mkdir /app
WORKDIR /app

COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY . /app

RUN chmod 777 start-server.sh

CMD ["./start-server.sh"]

EXPOSE 8000