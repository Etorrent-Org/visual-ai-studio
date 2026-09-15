FROM node:22-alpine AS frontend

WORKDIR /frontend
COPY web/package.json ./package.json
RUN npm install
COPY web/ ./
RUN npm run build

FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VISUAL_AI_DATA_DIR=/data \
    VISUAL_AI_WEB_DIST=/app/web-dist

WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY src/ ./src/
RUN pip install --no-cache-dir ".[web]"

COPY --from=frontend /frontend/dist /app/web-dist

RUN mkdir -p /data/projects

VOLUME ["/data"]
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=3)" || exit 1

CMD ["uvicorn", "visual_ai_studio.web_app:app", "--host", "0.0.0.0", "--port", "8000"]
