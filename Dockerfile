FROM python:3.13-alpine3.19 AS builder

# Configure Poetry
ENV POETRY_VERSION=2.1.1
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VENV=/opt/poetry-venv
ENV POETRY_CACHE_DIR=/opt/.cache

# Install poetry separated from system interpreter
RUN python3 -m venv $POETRY_VENV \
	&& $POETRY_VENV/bin/pip install -U pip setuptools \
	&& $POETRY_VENV/bin/pip install poetry==${POETRY_VERSION} 

# Add `poetry` to PATH
ENV PATH="${PATH}:${POETRY_VENV}/bin"

RUN poetry self add poetry-plugin-export==1.9.0

WORKDIR /app

# Install dependencies
COPY . ./
RUN poetry install 
RUN poetry run pytest
RUN poetry export -f requirements.txt --output requirements.txt



FROM python:3.13-alpine3.19 AS app

# Install python and build-dependencies for uWSGI
RUN apk add --update --no-cache python3 python3-dev py3-pip build-base linux-headers pcre-dev && ln -sf python3 /usr/bin/python

# Install pip, currently not needed, as installed by apk
# RUN python3 -m ensurepip
# RUN pip3 install --no-cache --upgrade pip setuptools

# Install dependencies
COPY --from=builder /app/requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip3 install --no-cache -r requirements.txt

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
