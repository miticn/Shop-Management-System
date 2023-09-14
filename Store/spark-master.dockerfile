FROM python:3

RUN mkdir -p /app
WORKDIR /app

COPY ./spark-master.py main.py
COPY ./configuration.py configuration.py
COPY ./requirements-spark.txt requirements.txt

RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "main.py" ]