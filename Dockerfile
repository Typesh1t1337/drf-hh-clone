FROM python:3.12-alpine

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1

ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt


RUN apk add --no-cache \
    gobject-introspection \
    pango-dev \
    pango \
    fontconfig \
    ttf-dejavu \
    cairo-dev


RUN pip install -r requirements.txt

COPY entrypoint.sh /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh

COPY . /usr/src/app/

RUN pip install daphne


CMD ["daphne", "-b", "0.0.0.0", "-p", "8001", "jobondemand.asgi:application"]

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
