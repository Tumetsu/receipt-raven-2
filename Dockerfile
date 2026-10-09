# Stage 1: build the frontend
FROM node:24-alpine AS frontend-builder

WORKDIR /app

# Workspace manifests first, so the dependency layer caches across source edits
COPY package.json package-lock.json ./
COPY frontend/package.json ./frontend/
RUN npm ci

COPY frontend/ ./frontend/
WORKDIR /app/frontend

# The image has no .git, so the commit shown in the app comes in as a build arg.
ARG BUILD_COMMIT=unknown
ENV BUILD_COMMIT=${BUILD_COMMIT}

# The API client and route tree are committed, so the build needs no backend.
RUN npm run build:ci

# Stage 2: backend, serving the built frontend
FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:0.8 /uv /bin/uv

ENV PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    PATH="/app/.venv/bin:$PATH" \
    ENVIRONMENT=production \
    PORT=8000 \
    DATABASE_URL=sqlite:////app/data/receipts.db \
    UPLOADS_DIR=/app/uploads \
    PAYEE_ACCOUNT_RULES_PATH=/app/config/payee-account-rules.json

WORKDIR /app

COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-dev

COPY backend/src ./src
COPY backend/alembic.ini ./
COPY backend/alembic ./alembic
COPY --from=frontend-builder /app/frontend/dist ./static

# Mount volumes over these to keep the database, the uploads and the rules.
RUN useradd --system --uid 1001 app \
    && mkdir -p /app/data /app/uploads /app/config \
    && chown -R app /app
USER app
VOLUME ["/app/data", "/app/uploads"]

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s \
  CMD python -c "import urllib.request,os; urllib.request.urlopen(f'http://127.0.0.1:{os.environ[\"PORT\"]}/health')"

# Migrations run on every start; Alembic is a no-op when the schema is current.
CMD ["sh", "-c", "alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port ${PORT}"]
