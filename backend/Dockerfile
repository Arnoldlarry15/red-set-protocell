FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Use gunicorn with uvicorn worker for production
# Worker count can be configured via WORKERS env var (default: 4)
CMD gunicorn -k uvicorn.workers.UvicornWorker \
    --workers ${WORKERS:-4} \
    --worker-connections ${WORKER_CONNECTIONS:-1000} \
    -b 0.0.0.0:${PORT:-8000} \
    app.api_server:app
