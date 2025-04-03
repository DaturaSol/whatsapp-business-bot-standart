# Dockerfile for my WhatsApp Bot

# 1. Get python image. 
# Sadly i could not find the Free Threaded image.
FROM python:3.13.2-slim

# 2. Set environment variables
# - Prevents Python from writing .pyc files;
# - Ensures Python output (like print) is sent straight to terminal without being buffered;
# - Configures Poetry installation location and behaviour.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \ 
    POETRY_VERSION=2.1.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    PATH="$POETRY_HOME/bin:$PATH"

# 3. Install system dependencies and Poetry
# - Update package list, install curl (needed for Poetry installer);
# - Download and run the official Poetry installation script <https://python-poetry.org/docs/#installing-with-the-official-installer>;
RUN apt-get update \
    && apt-get install --no-install-recommends -y curl \
    && curl -sSL https://install.python-poetry.org | python3 - --version ${POETRY_VERSION} \
    && apt-get purge -y --auto-remove curl \
    && rm -rf /var/lib/apt/lists/*

# 4. Set the working directory inside the container
WORKDIR /main

# 5. Copy only dependency definition files first (Leverages Docker cache)
COPY pyproject.toml poetry.lock* ./

# 6. Install project dependencies using Poetry
# --no-root: Installs only dependencies, not the project itself (standard behavior for install)
# --no-interaction / --no-ansi: Flags suitable for automated builds
# Add --no-dev flag if building a smaller production image (omits dev dependencies like pytest)
RUN poetry install --no-root --no-interaction --no-ansi --no-dev

# 7. Copy the application code into the container
COPY . .

# 8. Run the aplication
CMD ["poetry", "run", "uvicorn", "--host", "0.0.0.0", "--port", "$PORT", "src.main.py:app"]

