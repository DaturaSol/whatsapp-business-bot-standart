# Dockerfile for my WhatsApp Bot

# 1. Get python image. 
# Sadly i could not find the Free Threaded image.
FROM python:3.13.2-slim AS base

# 2. Set environment variables
# - Prevents Python from writing .pyc files;
# - Ensures Python output (like print) is sent straight to terminal without being buffered;
# - Configures Poetry installation location and behaviour.
# Poetry settings 
ENV POETRY_VERSION=2.1.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

ENV PATH="$POETRY_HOME/bin:$PATH"

WORKDIR /main

FROM base AS system-deps
RUN apt-get update \
    && apt-get install --no-install-recommends -y curl


FROM system-deps AS poetry-install    

RUN curl -sSL https://install.python-poetry.org | python3 - --version ${POETRY_VERSION}

FROM poetry-install AS clean-up

RUN apt-get purge -y --auto-remove curl \
    && rm -rf /var/lib/apt/lists/*

FROM clean-up AS app-deps

COPY pyproject.toml poetry.lock* ./

RUN poetry install --no-root --no-interaction --no-ansi

# 7. Copy the application code into the container
COPY . .

# 8. Run the aplication
CMD ["poetry", "run", "uvicorn", "--host", "0.0.0.0", "--port", "$PORT", "src.main.py:app"]

