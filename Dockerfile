FROM python:3.12

ENV PYTHONUNBUFFERED=1

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update && \
    apt-get install -y swig libssl-dev dpkg-dev netcat-openbsd

WORKDIR /code

COPY pyproject.toml uv.lock /code/

RUN uv sync --frozen --no-dev

COPY ./pairings/ /code/pairings/

WORKDIR /code/pairings

CMD ["uv", "run", "gunicorn", "pairings.wsgi"]
