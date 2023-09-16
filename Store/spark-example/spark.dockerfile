FROM bde2020/spark-python-template:3.3.0-hadoop3.3

COPY main.py /app/

ENV SPARK_APPLICATION_PYTHON_LOCATION /app/main.py
ENV SPARK_SUBMIT_ARGS "--driver-class-path /app/mysql-connector-j-8.0.33.jar --jars /app/mysql-connector-j-8.0.33.jar"

CMD [ "spark-submit", "--jars", "/app/mysql-connector-j-8.0.33.jar", "/app/main.py"]