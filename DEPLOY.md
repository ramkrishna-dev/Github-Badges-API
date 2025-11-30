# Deployment Guide

## Docker

```bash
docker build -t github-badge-api .
docker run -p 8000:8000 github-badge-api
```

## Docker Compose

```bash
docker-compose up -d
```

## Kubernetes

```bash
kubectl apply -f k8s/
```

## PythonAnywhere

1. Upload code
2. Install requirements: `pip install -e .`
3. Run: `uvicorn src.main:app --host 0.0.0.0 --port 8000`

## Render.com

1. Connect GitHub repo
2. Set build command: `pip install -e .`
3. Start command: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`

## Fly.io

```bash
fly launch
fly deploy
```

## Environment Variables

```env
GITHUB_TOKEN=your_token
REDIS_URL=redis://localhost:6379
SECRET_KEY=your_secret
```