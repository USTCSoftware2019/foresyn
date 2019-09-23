FROM python:3.6

RUN mkdir /app
WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt --no-cache-dir
RUN sed -i '34 s/^/#/; 35 s/^/#/; 36 s/^/#/' /usr/local/lib/python3.6/site-packages/django/db/backends/mysql/base.py && sed -i 's/.decode(errors/.encode(errors/g' /usr/local/lib/python3.6/site-packages/django/db/backends/mysql/operations.py && wget -O /wait.sh https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh && chmod +x /wait.sh
COPY ./docker/run.sh /run.sh
