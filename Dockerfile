FROM python:3.6

RUN mkdir /app
WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt --no-cache-dir
RUN sed -i '35 s/^/#/; 36 s/^/#/; 37 s/^/#/' /usr/local/lib/python3.6/site-packages/django/db/backends/mysql/base.py && sed -i 's/.decode(errors/.encode(errors/g' /usr/local/lib/python3.6/site-packages/django/db/backends/mysql/operations.py && wget -O /wait.sh https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh && chmod +x /wait.sh
RUN apt update && apt install libmysqlclient-dev
WORKDIR /my_trgm
RUN make my_trgm.so && make copy && make install
COPY ./docker/run.sh /run.sh
