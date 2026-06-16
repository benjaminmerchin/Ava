# Ava backend — FastAPI + CrewAI. Build from the repo ROOT:
#   docker build -f backend/Dockerfile -t ava-backend .
FROM python:3.12-slim

WORKDIR /srv
COPY backend/requirements.txt /srv/backend/requirements.txt
RUN pip install --no-cache-dir -r /srv/backend/requirements.txt

COPY backend /srv/backend
COPY widget /srv/widget
COPY docs /srv/docs
COPY demo /srv/demo

WORKDIR /srv/backend
ENV PORT=8000
EXPOSE 8000
# TFY_BASE_URL / TFY_API_KEY / MODEL_PRIMARY are injected as platform env vars
# (never baked into the image — backend/.env is .dockerignored).
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
