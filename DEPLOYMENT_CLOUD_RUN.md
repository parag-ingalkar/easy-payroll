# Google Cloud Run Deployment Guide

This guide describes how to deploy the application as **two separate Google Cloud Run services**: one for the Next.js frontend and one for the FastAPI backend.

## Architecture Overview

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│   Browser       │ ──────► │   Frontend      │ ──────► │   Backend       │
│                 │         │   (Cloud Run)   │         │   (Cloud Run)   │
│                 │         │   Port: 8080    │         │   Port: 8080    │
└─────────────────┘         └─────────────────┘         └────────┬────────┘
                                                                  │
                                                                  ▼
                                                         ┌─────────────────┐
                                                         │   Cloud SQL     │
                                                         │   PostgreSQL    │
                                                         └─────────────────┘
```

### Service Boundaries

| Service | Responsibility | Public? | Port | Talks to |
|---------|---------------|---------|------|----------|
| Frontend | Next.js UI, SSR, static assets | Yes | 8080 | Backend URL |
| Backend | FastAPI API, auth, DB access | Yes | 8080 | Cloud SQL |

## Prerequisites

1. **Google Cloud Project** with billing enabled
2. **gcloud CLI** installed and authenticated
3. **Docker** installed locally (optional, for testing)
4. **Git** repository connected to GitHub

## Step 1: Enable Required APIs

```bash
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  iamcredentials.googleapis.com \
  secretmanager.googleapis.com \
  sqladmin.googleapis.com \
  --project YOUR_PROJECT_ID
```

## Step 2: Create Artifact Registry

```bash
gcloud artifacts repositories create app-images \
  --repository-format=docker \
  --location=europe-west3 \
  --description="Docker images for frontend and backend" \
  --project YOUR_PROJECT_ID
```

## Step 3: Create Runtime Service Accounts

```bash
# Backend service account
gcloud iam service-accounts create backend-runtime \
  --display-name "Backend Runtime SA" \
  --project YOUR_PROJECT_ID

# Frontend service account
gcloud iam service-accounts create frontend-runtime \
  --display-name "Frontend Runtime SA" \
  --project YOUR_PROJECT_ID

# Grant Cloud SQL Client role to backend
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member "serviceAccount:backend-runtime@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role "roles/cloudsql.client"

# Grant Secret Manager access to backend
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member "serviceAccount:backend-runtime@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role "roles/secretmanager.secretAccessor"
```

## Step 4: Provision Cloud SQL PostgreSQL

```bash
# Create Cloud SQL instance
gcloud sql instances create APP_DB \
  --database-version=POSTGRES_16 \
  --tier=db-f1-micro \
  --region=europe-west3 \
  --root-password=YOUR_ROOT_PASSWORD \
  --project YOUR_PROJECT_ID

# Create database
gcloud sql databases create postgresdb \
  --instance=APP_DB \
  --project YOUR_PROJECT_ID

# Create database user
gcloud sql users create postgresuser \
  --instance=APP_DB \
  --password=YOUR_USER_PASSWORD \
  --project YOUR_PROJECT_ID
```

## Step 5: Store Secrets in Secret Manager

```bash
# Store backend SECRET_KEY
echo "YOUR_GENERATED_SECRET_KEY_MIN_32_CHARS" | \
  gcloud secrets create backend-secret \
  --data-file=- \
  --project YOUR_PROJECT_ID
```

## Step 6: Configure Workload Identity Federation for GitHub

### 6.1 Create Deployer Service Account

```bash
gcloud iam service-accounts create github-deployer \
  --display-name "GitHub Deployer SA" \
  --project YOUR_PROJECT_ID
```

### 6.2 Grant Required Roles

```bash
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member "serviceAccount:github-deployer@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role "roles/run.admin"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member "serviceAccount:github-deployer@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role "roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member "serviceAccount:github-deployer@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role "roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member "serviceAccount:github-deployer@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role "roles/secretmanager.secretAccessor"
```

### 6.3 Create Workload Identity Pool

```bash
gcloud iam workload-identity-pools create "github-pool" \
  --project="YOUR_PROJECT_ID" \
  --location="global" \
  --display-name="GitHub Actions Pool"

gcloud iam workload-identity-pools providers create-oidc "github-provider" \
  --project="YOUR_PROJECT_ID" \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --display-name="GitHub Provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
  --issuer-uri="https://token.actions.githubusercontent.com"
```

### 6.4 Allow GitHub to Impersonate Deployer SA

```bash
gcloud iam service-accounts add-iam-policy-binding github-deployer@YOUR_PROJECT_ID.iam.gserviceaccount.com \
  --project YOUR_PROJECT_ID \
  --role roles/iam.workloadIdentityUser \
  --member "principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/attribute.repository/YOUR_GITHUB_ORG/YOUR_REPO_NAME"
```

## Step 7: Configure GitHub Repository

### 7.1 Add Repository Variables

Go to your GitHub repo → Settings → Actions → Variables → New repository variable:

| Name | Value |
|------|-------|
| `GCP_PROJECT_ID` | Your GCP project ID |
| `GCP_REGION` | `europe-west3` (or your region) |
| `ARTIFACT_REGISTRY_REPO` | `app-images` |
| `FRONTEND_SERVICE_NAME` | `frontend-service` |
| `BACKEND_SERVICE_NAME` | `backend-service` |
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | `projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/providers/github-provider` |
| `GCP_DEPLOYER_SERVICE_ACCOUNT` | `github-deployer@YOUR_PROJECT_ID.iam.gserviceaccount.com` |

### 7.2 Update Database Connection String

In the deploy workflow, update the Cloud SQL instance name from `APP_DB` to your actual instance name.

## Step 8: Environment Configuration

### Backend Environment Variables

The backend uses these environment variables (set via `--set-env-vars` in Cloud Run):

| Variable | Description | Example |
|----------|-------------|---------|
| `PORT` | Server port (Cloud Run sets this) | `8080` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+psycopg://user:pass@/dbname?host=/cloudsql/project:region:instance` |
| `SECRET_KEY` | JWT signing key (from Secret Manager) | *secret* |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token expiry | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token expiry | `7` |
| `FRONTEND_URLS` | Allowed CORS origins | `https://frontend-service-xxx.a.run.app` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Frontend Environment Variables

The frontend uses these environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `PORT` | Server port (Cloud Run sets this) | `8080` |
| `NODE_ENV` | Environment | `production` |
| `NEXT_PUBLIC_API_BASE_URL` | Backend service URL | `https://backend-service-xxx.a.run.app` |
| `BACKEND_URL` | Backend URL for server-side calls | `https://backend-service-xxx.a.run.app` |
| `NEXT_PUBLIC_FRONTEND_URL` | Frontend URL | `https://frontend-service-xxx.a.run.app` |

## Step 9: Manual Deployment (Optional)

### Build and Deploy Backend

```bash
cd backend

# Build Docker image
docker build -t europe-west3-docker.pkg.dev/YOUR_PROJECT_ID/app-images/backend:latest .

# Push to Artifact Registry
docker push europe-west3-docker.pkg.dev/YOUR_PROJECT_ID/app-images/backend:latest

# Deploy to Cloud Run
gcloud run deploy backend-service \
  --image europe-west3-docker.pkg.dev/YOUR_PROJECT_ID/app-images/backend:latest \
  --region europe-west3 \
  --platform managed \
  --port 8080 \
  --allow-unauthenticated \
  --set-env-vars FRONTEND_URLS=https://frontend-service-xxx.a.run.app \
  --set-secrets SECRET_KEY=backend-secret:latest \
  --add-cloudsql-instances YOUR_PROJECT_ID:europe-west3:APP_DB \
  --service-account backend-runtime@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

### Build and Deploy Frontend

```bash
cd frontend

# Build Docker image
docker build -t europe-west3-docker.pkg.dev/YOUR_PROJECT_ID/app-images/frontend:latest .

# Push to Artifact Registry
docker push europe-west3-docker.pkg.dev/YOUR_PROJECT_ID/app-images/frontend:latest

# Deploy to Cloud Run
gcloud run deploy frontend-service \
  --image europe-west3-docker.pkg.dev/YOUR_PROJECT_ID/app-images/frontend:latest \
  --region europe-west3 \
  --platform managed \
  --port 8080 \
  --allow-unauthenticated \
  --set-env-vars NEXT_PUBLIC_API_BASE_URL=https://backend-service-xxx.a.run.app \
  --set-env-vars BACKEND_URL=https://backend-service-xxx.a.run.app \
  --service-account frontend-runtime@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

## Step 10: Automated Deployment via GitHub Actions

Once configured, pushing to `main` branch will automatically:

1. Detect which files changed (backend or frontend)
2. Build only the affected service(s)
3. Push images to Artifact Registry
4. Deploy to Cloud Run
5. Run smoke tests

### Deployment Order

- **Backend deploys first** (frontend depends on backend API)
- **Frontend deploys second** (after backend health checks pass)

## CORS Configuration

### How CORS Works in This Setup

With two separate Cloud Run services, browser requests from frontend to backend are **cross-origin**. The backend CORS middleware is configured to allow requests from the frontend service URL.

**Backend CORS settings:**
- Reads `FRONTEND_URLS` environment variable (comma-separated list)
- Allows credentials (cookies) for refresh token flow
- Configured in `backend/app/core/config.py` and `backend/app/main.py`

**Example:**
```bash
FRONTEND_URLS=https://frontend-service-xxx.a.run.app,https://your-custom-domain.com
```

### Testing CORS Locally

```bash
# Start backend
cd backend
uv run fastapi dev app.main:app --port 8000

# Start frontend (in another terminal)
cd frontend
bun run dev

# Frontend should call http://localhost:8000 via rewrites in next.config.ts
```

## Post-Deployment Verification

### 1. Check Backend Health

```bash
curl https://backend-service-xxx.a.run.app/health
# Expected: {"status":"healthy","service":"backend"}
```

### 2. Check Frontend Loads

```bash
curl https://frontend-service-xxx.a.run.app/
# Expected: HTML content
```

### 3. Test API Call from Frontend

Open browser console on frontend URL and check network tab for successful API calls.

### 4. Verify Cloud Logging

```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=backend-service" --limit 10
```

## Troubleshooting

### Backend Won't Start

1. Check logs: `gcloud run services logs read backend-service --region europe-west3 --limit 50`
2. Verify DATABASE_URL format for Cloud SQL
3. Ensure Cloud SQL instance has the correct IAM permissions

### Frontend Can't Connect to Backend

1. Verify `NEXT_PUBLIC_API_BASE_URL` is set correctly
2. Check CORS settings on backend (`FRONTEND_URLS`)
3. Ensure backend service is publicly accessible (`--allow-unauthenticated`)

### Database Migration Fails

1. Check Cloud SQL connection string format
2. Verify service account has Cloud SQL Client role
3. Ensure Cloud SQL instance allows connections from Cloud Run

### Cold Start Issues

If experiencing slow cold starts:
- Set `--min-instances=1` to keep at least one instance warm
- Increase memory/CPU allocation
- Optimize application startup time

## Rollback

To rollback to a previous revision:

```bash
gcloud run services update-traffic backend-service \
  --to-revisions=PREVIOUS_REVISION_ID=100 \
  --region europe-west3
```

## Cost Optimization

- Use `--min-instances=0` for non-production environments
- Set appropriate `--max-instances` limits
- Consider Cloud Run jobs for batch operations
- Monitor usage in Cloud Console

## Security Best Practices

1. **Use Secret Manager** for all sensitive values
2. **Principle of least privilege** for service accounts
3. **Enable VPC Service Controls** if needed
4. **Use custom domains** with Cloud Armor for DDoS protection
5. **Regular security updates** to dependencies

## Next Steps

After successful deployment:

1. Set up custom domain with Cloud Load Balancing
2. Configure Cloud Monitoring alerts
3. Set up automated backups for Cloud SQL
4. Implement rate limiting
5. Add distributed tracing with Cloud Trace
