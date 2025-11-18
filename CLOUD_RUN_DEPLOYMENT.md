# Google Cloud Run Deployment Guide

This repository includes a ready-to-run deployment flow for the Job Hunting AI backend on Google Cloud Run.

Overview
- Recommended (automated): run `./deploy-cloudrun.sh`, which uses Cloud Build (`cloudbuild.yaml`) to build, push, and deploy.
- Local build & push: you can build locally and push to Container Registry, but CI / Cloud Build is the canonical path.

Prerequisites
- A Google Cloud project with billing enabled
- `gcloud` CLI installed and authenticated
- Docker or an alternative runtime (Colima) if building locally

Quick start (recommended)
1. Run the deploy script and follow prompts:

```bash
./deploy-cloudrun.sh
````

2. The script will submit a Cloud Build using `cloudbuild.yaml`, which builds the image, pushes it to Container Registry, and deploys to Cloud Run.

Manual steps (optional)

- To submit the build yourself:

```bash
gcloud builds submit --config cloudbuild.yaml
```

- To deploy a specific image to Cloud Run:

```bash
gcloud run deploy job-hunting-ai-backend \
  --image gcr.io/YOUR-PROJECT-ID/job-hunting-ai-backend:latest \
  --region us-west1 --platform managed --allow-unauthenticated \
  --port 8080 --memory 2Gi --cpu 2 --timeout 300 \
  --set-env-vars "FLASK_ENV=production,PYTHONUNBUFFERED=1,ADZUNA_APP_ID=...,ADZUNA_APP_KEY=...,SECRET_KEY=..."
```

Local testing

```bash
docker build -t job-hunting-ai-backend:test .
docker run -p 8080:8080 \
  -e ADZUNA_APP_ID=your_app_id -e ADZUNA_APP_KEY=your_app_key \
  -e SECRET_KEY=your_secret_key -e FLASK_ENV=production \
  job-hunting-ai-backend:test
curl http://localhost:8080/health
```

Troubleshooting & notes

- If the container won't start, check logs:

```bash
gcloud run services logs read job-hunting-ai-backend --region=us-west1 --limit=50
gcloud run services logs tail job-hunting-ai-backend --region=us-west1
```

- For production secrets, use Secret Manager and `--update-secrets` instead of embedding secrets on the command line.

