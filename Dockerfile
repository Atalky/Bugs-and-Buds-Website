FROM python:3.13-slim

WORKDIR /app

# install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# install deps first so this layer caches independently of app code changes
COPY pyproject.toml uv.lock ./

# Sync dependencies and exclude the app itself from this layer's build
RUN uv sync --frozen --no-dev

# now the actual app
COPY . .

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
