FROM python:3.7-alpine


ENV PYTHONUNBUFFRED 1

COPY ./requirements.txt /requirements.txt
RUN pip install -r requirements.txt


RUN mkdir /app 
WORKDIR /app
COPY ./app /

RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static
RUN adduser -D user
RUN chown -R user:user /vol/
RUN chown -R 755 /vol/web
USER user