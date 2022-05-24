FROM alpine:3.16.0

# Install python and build-dependencies for uWSGI
RUN apk add --update --no-cache python3 python3-dev build-base linux-headers pcre-dev && ln -sf python3 /usr/bin/python

# Install pip
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools

# Install dependencies
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --no-cache -r requirements.txt

# Install application and configs
COPY . /app
RUN chmod +x ./start.sh

# Add user for webserver
# 82 is the standard uid/gid for "www-data" in Alpine
RUN set -x \
    #&& addgroup -g 82 -S www-data \
    && adduser -u 82 -D -S -G www-data www-data

EXPOSE 9090

CMD ["./start.sh"]
