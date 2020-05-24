FROM python:3.6

RUN apt-get update
RUN mkdir /code
COPY requirements.txt /code/requirements.txt
RUN pip3 install -r /code/requirements.txt
COPY runner.sh /code/runner.sh
COPY meow.py /code/meow.py
WORKDIR /code
CMD "./runner.sh"