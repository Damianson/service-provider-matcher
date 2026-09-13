#!/usr/bin/env bash
# ==============================================================================
# Google Cloud Run Deployment Script for Service-Provider Matcher
# ==============================================================================
set -e

SERVICE_NAME="service-provider-matcher"
REGION="${GCP_REGION:-us-central1}"

echo "========================================================"
echo " Deploying ${SERVICE_NAME} to GCP Cloud Run"
echo "========================================================"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "Error: 'gcloud' CLI is not installed or not in PATH."
    echo "Please install the Google Cloud SDK: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ] || [ "$PROJECT_ID" = "(unset)" ]; then
    echo "Error: No active GCP project configured."
    echo "Run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo "Active Project: ${PROJECT_ID}"
echo "Region:         ${REGION}"
echo ""

# Enable required GCP APIs
echo "Ensuring Cloud Run and Cloud Build APIs are enabled..."
gcloud services enable run.googleapis.com cloudbuild.googleapis.com --project="${PROJECT_ID}"

# Prepare env vars if present
ENV_VARS_FLAG=""
if [ -n "$GEMINI_API_KEY" ]; then
    ENV_VARS_FLAG="--set-env-vars GEMINI_API_KEY=${GEMINI_API_KEY}"
fi

# Deploy using source (Cloud Build builds the Dockerfile directly in Cloud)
echo "Building and deploying container from source to Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
    --source . \
    --region "${REGION}" \
    --platform managed \
    --allow-unauthenticated \
    --memory 512Mi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 2 \
    ${ENV_VARS_FLAG}

echo ""
echo "========================================================"
echo " Deployment Complete!"
echo " Service URL:"
gcloud run services describe "${SERVICE_NAME}" --platform managed --region "${REGION}" --format 'value(status.url)'
echo "========================================================"

