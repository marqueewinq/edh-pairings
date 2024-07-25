FROM    python:3.7

ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN apt-get install -y swig libssl-dev dpkg-dev netcat-openbsd

WORKDIR /code

ADD requirements.txt /code/

RUN pip3 install --upgrade pip && \
    pip3 install -r requirements.txt

COPY ./pairings/ /code/pairings/

CMD ["gunicorn", "pairings.wsgi"]
