FROM python:3.13.2-slim AS base

# Basic System Configs 
ENV POETRY_VERSION=2.1.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    # No virtual enviroments here, it is on a container
    POETRY_VIRTUALENVS_CREATE=false \
    # Dont forget to ADD PYTHONPATH.
    PYTHONPATH="/main/src" 

# This part must be set after afterwards, otherwise  
# docker wont know where `$POETRY_HOME` is!
ENV PATH="$POETRY_HOME/bin:$PATH"

WORKDIR /main

# System dependancies
FROM base AS system-deps
RUN apt-get update \
    && apt-get install --no-install-recommends -y curl

# Install Poetry
FROM system-deps AS poetry-install    
RUN curl -sSL https://install.python-poetry.org | python3 - --version ${POETRY_VERSION}

# Clean Garbage
FROM poetry-install AS clean-up
RUN apt-get purge -y --auto-remove curl \
    && rm -rf /var/lib/apt/lists/*

# App dependancies such as pyproject.toml from `./`
FROM clean-up AS app-deps
COPY pyproject.toml poetry.lock* ./

# Install poetry dependancies
RUN poetry install --no-root --no-interaction --no-ansi

# Copy the application code into the container
COPY . .

# Run the aplication
CMD ["poetry", "run", "uvicorn", "--host", "0.0.0.0", "--port", "8080", "src.main:app"]

