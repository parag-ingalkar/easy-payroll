# Production Deployment Guide

This guide covers deploying the application to **Google Cloud Run** and **AWS** (via Docker containers). The application is containerized with both frontend and backend in a single image for simplified deployment.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [CORS Configuration](#cors-configuration)
3. [Environment Variables](#environment-variables)
4. [Building the Docker Image](#building-the-docker-image)
5. [Google Cloud Run Deployment](#google-cloud-run-deployment)
6. [AWS Deployment Options](#aws-deployment-options)
7. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

The application uses a **single-container architecture**:
- **Backend**: FastAPI server running on port 8000 (configurable via `PORT`)
- **Frontend**: Next.js standalone server running on port 3000
- **API Proxy**: Next.js rewrites `/api/*` requests to the backend, making them same-origin from the browser's perspective

**Key Benefit**: This architecture eliminates CORS issues because the browser only makes same-origin requests to the frontend, which proxies API calls internally.

```
┌─────────────────┐
│     Browser     │
└────────┬────────┘
         │
         │ https://your-domain.com
         │ (all requests same-origin)
         ▼
┌─────────────────────────────────────┐
│      Single Container (Cloud Run)   │
│  ┌─────────────┐    ┌─────────────┐ │
│  │  Frontend   │───▶│   Backend   │ │
│  │  (Port 3000)│    │  (Port 8000)│ │
│  │             │ /api/*           │ │
│  └─────────────┘    └─────────────┘ │
└─────────────────────────────────────┘
         │
         │ DATABASE_URL
         ▼
┌─────────────────┐
│  Cloud SQL /    │
│  RDS PostgreSQL │
└─────────────────┘
```

---

## CORS Configuration

### How CORS Works in This Setup

**Good news**: You typically **don't need to worry about CORS** with this architecture because:

1. **Next.js rewrites** proxy all `/api/*` requests to the backend
2. From the browser's perspective, all requests are **same-origin** (to the frontend)
3. The backend-to-frontend communication happens server-side within the container

### When CORS Matters

CORS configuration is still important for:
- **Direct API access** (e.g., mobile apps, third-party integrations)
- **Development environments** where frontend/backend run separately
- **Future microservices** architectures

### Configuring Allowed Origins

Set the `FRONTEND_URLS` environment variable (comma-separated list):

```bash
# Development
FRONTEND_URLS=http://localhost:3000

# Production with multiple domains
FRONTEND_URLS=https://myapp.com,https://www.myapp.com,https://staging.myapp.com

# Development + Production
FRONTEND_URLS=http://localhost:3000,https://myapp.com
```

**Example for Cloud Run:**
```bash
gcloud run services update my-app \
  --set-env-vars FRONTEND_URLS=https://my-app-abc123.a.run.app
```

---

## Environment Variables

### Backend Variables (Required)

Create a `.env` file or set these as environment variables in your cloud platform:

```bash
# Database (REQUIRED)
DATABASE_URL=postgresql+psycopg://user:password@host:5432/dbname

# Security (REQUIRED - generate strong secrets)
SECRET_KEY=generate-a-strong-random-secret-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS (REQUIRED)
FRONTEND_URLS=https://your-app.a.run.app

# Optional
LOG_LEVEL=INFO
```

### Frontend Variables (Required)

```bash
# Backend URL for Next.js rewrites
# For single-container deployment, use localhost
BACKEND_URL=http://localhost:8000

# Frontend URL (for meta tags, etc.)
NEXT_PUBLIC_FRONTEND_URL=https://your-app.a.run.app

# App name
NEXT_PUBLIC_APP_NAME="Your App"
```

**Note**: In the single-container setup, `BACKEND_URL` should be `http://localhost:8000` because both services run in the same container.

---

## Building the Docker Image

### Local Build

```bash
# Build the image
docker build -t my-app:latest .

# Test locally
docker run -p 3000:3000 -p 8000:8000 \
  -e DATABASE_URL="postgresql+psycopg://..." \
  -e SECRET_KEY="your-secret-key" \
  -e FRONTEND_URLS="http://localhost:3000" \
  -e BACKEND_URL="http://localhost:8000" \
  my-app:latest
```

Visit `http://localhost:3000` to test.

### Push to Container Registry

#### Google Container Registry (GCR)

```bash
# Tag the image
docker tag my-app:latest gcr.io/YOUR_PROJECT_ID/my-app:latest

# Push to GCR
docker push gcr.io/YOUR_PROJECT_ID/my-app:latest
```

#### Amazon Elastic Container Registry (ECR)

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Tag the image
docker tag my-app:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/my-app:latest

# Push to ECR
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/my-app:latest
```

---

## Google Cloud Run Deployment

### Prerequisites

1. Google Cloud project with billing enabled
2. Cloud SQL PostgreSQL instance (or external database)
3. Service account with appropriate permissions

### Step 1: Create Cloud SQL Database

```bash
# Create Cloud SQL instance
gcloud sql instances create my-app-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1 \
  --root-password=your-root-password

# Create database
gcloud sql databases create myapp --instance=my-app-db

# Create user
gcloud sql users create myappuser \
  --instance=my-app-db \
  --password=user-password
```

### Step 2: Configure Service Account

```bash
# Create service account
gcloud iam service-accounts create my-app-sa \
  --display-name="My App Service Account"

# Grant Cloud SQL Client role
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:my-app-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudsql.client"
```

### Step 3: Deploy to Cloud Run

```bash
gcloud run deploy my-app \
  --image gcr.io/YOUR_PROJECT_ID/my-app:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 3000 \
  --set-env-vars "DATABASE_URL=postgresql+psycopg://myappuser:user-password@/myapp?host=/cloudsql/YOUR_PROJECT_ID:us-central1:my-app-db" \
  --set-env-vars "SECRET_KEY=$(openssl rand -hex 32)" \
  --set-env-vars "FRONTEND_URLS=https://my-app-abc123.a.run.app" \
  --set-env-vars "BACKEND_URL=http://localhost:8000" \
  --set-env-vars "NEXT_PUBLIC_FRONTEND_URL=https://my-app-abc123.a.run.app" \
  --service-account my-app-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com \
  --add-cloudsql-instances YOUR_PROJECT_ID:us-central1:my-app-db \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --timeout 300 \
  --concurrency 80
```

**Important Notes:**
- `--port 3000`: Cloud Run will route traffic to the frontend port
- `--add-cloudsql-instances`: Enables connection to Cloud SQL via Unix socket
- Database URL uses Unix socket path for Cloud SQL connection

### Step 4: Update CORS After Deployment

After deployment, update `FRONTEND_URLS` with your Cloud Run URL:

```bash
gcloud run services update my-app \
  --region us-central1 \
  --set-env-vars FRONTEND_URLS=https://my-app-abc123.a.run.app
```

### Step 5: Custom Domain (Optional)

```bash
# Map custom domain
gcloud beta run domain-mappings create \
  --service my-app \
  --domain myapp.com \
  --region us-central1
```

Then update `FRONTEND_URLS` to include your custom domain.

---

## AWS Deployment Options

### Option 1: AWS App Runner (Simplest)

```bash
# Using AWS Console or CLI
aws apprunner create-service \
  --service-name my-app \
  --source-configuration ImageRepositoryConfiguration={ImageIdentifier=YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/my-app:latest,ImageConfiguration={Port=3000,Cpu=1,Memory=2048}} \
  --instance-configuration Cpu=1,Memory=2048 \
  --health-check-configuration Protocol=HTTP,Path=/health,Interval=30,Timeout=10,HealthyThreshold=3,UnhealthyThreshold=3 \
  --auto-configuration-allowed
```

Set environment variables in the AWS Console after creation.

### Option 2: AWS ECS Fargate

Create a task definition with two containers (frontend + backend) or use the single container approach.

**Task Definition (JSON):**
```json
{
  "family": "my-app",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "app",
      "image": "YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/my-app:latest",
      "portMappings": [
        {"containerPort": 3000, "protocol": "tcp"}
      ],
      "environment": [
        {"name": "DATABASE_URL", "value": "postgresql+psycopg://..."},
        {"name": "SECRET_KEY", "value": "your-secret"},
        {"name": "FRONTEND_URLS", "value": "https://your-domain.com"},
        {"name": "BACKEND_URL", "value": "http://localhost:8000"}
      ],
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 10,
        "retries": 3
      }
    }
  ]
}
```

### Option 3: AWS Lambda (Not Recommended)

This app is not optimized for Lambda due to:
- Cold start times with Python + Node.js
- Database connection pooling challenges
- Long-running processes (migrations)

Use **App Runner** or **ECS Fargate** instead.

---

## Troubleshooting

### CORS Errors in Browser Console

**Symptom**: `Access to fetch at '...' from origin '...' has been blocked by CORS policy`

**Solutions**:
1. Verify `FRONTEND_URLS` includes your frontend domain (comma-separated if multiple)
2. Check that Next.js rewrites are working: visit `/api/health` in browser - should return backend response
3. Ensure `BACKEND_URL` is set correctly in the container

### Database Connection Errors

**Symptom**: Migration fails or app can't connect to database

**Solutions**:
1. **Cloud SQL**: Verify `--add-cloudsql-instances` flag and Unix socket path in `DATABASE_URL`
2. **External DB**: Ensure VPC connectivity and firewall rules allow connections
3. Check credentials in `DATABASE_URL`

### Health Check Failures

**Symptom**: Cloud Run/ECS reports unhealthy

**Solutions**:
1. Verify health endpoint: `curl http://localhost:8000/health`
2. Check logs for startup errors
3. Increase `--timeout` or `HEALTHCHECK` start period

### Frontend Can't Reach Backend

**Symptom**: API requests fail with network errors

**Solutions**:
1. Verify `BACKEND_URL=http://localhost:8000` (for single-container setup)
2. Check that both services are running: `ps aux | grep -E "(fastapi|server.js)"`
3. Review Next.js rewrites in `next.config.ts`

### Token/Cookie Issues

**Symptom**: Authentication doesn't persist or refresh fails

**Solutions**:
1. Ensure `allow_credentials=True` in CORS middleware (already configured)
2. Verify `credentials: "include"` in frontend API calls (already in `api.ts`)
3. Check that secure cookies work over HTTPS in production

---

## Quick Reference Commands

### Google Cloud Run

```bash
# View logs
gcloud run services logs read my-app --region us-central1 --limit 50

# Update environment variables
gcloud run services update my-app \
  --region us-central1 \
  --set-env-vars KEY=value

# Rollback to previous revision
gcloud run services update-traffic my-app \
  --region us-central1 \
  --to-revisions=PREVIOUS_REVISION_ID=100

# Delete service
gcloud run services delete my-app --region us-central1
```

### Docker

```bash
# Rebuild without cache
docker build --no-cache -t my-app:latest .

# Run with all env vars
docker run --rm -it \
  -p 3000:3000 \
  -e DATABASE_URL="..." \
  -e SECRET_KEY="..." \
  -e FRONTEND_URLS="http://localhost:3000" \
  -e BACKEND_URL="http://localhost:8000" \
  my-app:latest

# Inspect container
docker exec -it CONTAINER_ID bash
```

---

## Security Checklist

- [ ] Generate strong `SECRET_KEY` (min 32 characters, random)
- [ ] Use environment variables for all secrets (never commit to git)
- [ ] Enable HTTPS for all production domains
- [ ] Restrict database access to application only
- [ ] Use private container registry
- [ ] Enable Cloud Run/ECS IAM authentication
- [ ] Set up monitoring and alerting
- [ ] Regular security updates (rebuild images monthly)

---

## Next Steps After Deployment

1. **Set up monitoring**: Cloud Monitoring, Datadog, or Sentry
2. **Configure backups**: Automated database backups
3. **Set up CI/CD**: GitHub Actions, Cloud Build, or CodePipeline
4. **Add custom domain**: With SSL certificate
5. **Configure logging**: Structured logs for better debugging
6. **Set up alerts**: For errors, latency, and downtime

For support or questions, refer to the application logs and cloud provider documentation.
