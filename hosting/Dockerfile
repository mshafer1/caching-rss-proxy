FROM python@sha256:66bb49690f06388ea14426e4522c8a4b81b4a66610568bb12c79583a8b3024b9 AS poetry_installed

RUN apk update && apk add --no-cache curl python3-dev libressl-dev gcc libc6-compat rust libc-dev cargo pkgconf py3-openssl

RUN python3 -m pip install poetry poetry-plugin-export

FROM poetry_installed AS requirements_listed

COPY app/pyproject.toml app/poetry.lock ./

RUN poetry export -o requirements.txt

FROM python@sha256:66bb49690f06388ea14426e4522c8a4b81b4a66610568bb12c79583a8b3024b9 AS APP

RUN apk update && apk add --no-cache python3-dev build-base linux-headers

WORKDIR /app

COPY ./hosting/config/wsgi.ini ./

COPY --from=requirements_listed requirements.txt ./

RUN python3 -m pip install -r requirements.txt

COPY ./app /app

RUN python3 -m pip install -e .

CMD [ "uwsgi", "--ini", "/app/wsgi.ini"]
