FROM docker.io/library/node:14 as frontend-builder
WORKDIR /app/web

COPY ./web/package.json ./web/package-lock.json* ./
RUN --mount=type=cache,target=/app/web/node_modules \
    --mount=type=cache,target=/root/.npm \
    npm install --production

COPY ./web ./
RUN --mount=type=cache,target=/app/web/node_modules \
    --mount=type=cache,target=/root/.npm \
    npm --unsafe-perm run build


FROM python:3.9-slim as python-base

FROM python-base as python-builder
WORKDIR /app

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        # deps for installing poetry
        curl \
        # deps for building python deps
        build-essential \
        # used by poetry to install python deps
        git

RUN curl -sSL https://install.python-poetry.org | \
    env POETRY_VERSION=1.5.0 python

# Install the Python dependencies
COPY pyproject.toml poetry.toml poetry.lock README.md ./
COPY ai_librarian ./ai_librarian
RUN /root/.local/bin/poetry install

FROM python-base as production
WORKDIR /app

COPY --from=python-builder /app ./

ENV PATH="/app/.venv/bin:$PATH"

COPY --from=frontend-builder /app/web/dist /app/web/dist

# COPY ./ai_librarian ./ai_librarian

# Set environment variables
ENV HOST 0.0.0.0
ENV PORT 8000
ENV DATA_DIR /data

# Expose the specified port
#
# Note: This is only valid for default port. If you change the port
# via runtime environment variable, you may want to expose/publish it
# manually.
EXPOSE 8000

CMD ["sh", "-c", "gunicorn --bind ${HOST}:${PORT} ai_librarian.web:app"]
