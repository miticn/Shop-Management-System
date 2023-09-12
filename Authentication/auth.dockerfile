FROM python:3

RUN mkdir -p /app
WORKDIR /app

COPY ./main.py main.py
COPY ./configuration.py configuration.py
COPY ./models.py models.py
COPY ./requirements.txt requirements.txt

RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "main.py" ]