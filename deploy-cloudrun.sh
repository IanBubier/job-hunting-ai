#!/bin/bash

# Deployment script for Google Cloud Run
# This script helps you deploy the Job Hunting AI backend to Google Cloud Run

set -e

echo "================================================"
echo "Google Cloud Run Deployment Script"
echo "================================================"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "Error: gcloud CLI is not installed."
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Set your Google Cloud project ID
read -p "Enter your Google Cloud Project ID: " PROJECT_ID

if [ -z "$PROJECT_ID" ]; then
    echo "Error: Project ID cannot be empty"
    exit 1
fi

# Set the region (default: us-west1)
read -p "Enter your preferred region [us-west1]: " REGION
REGION=${REGION:-us-west1}

# Set the service name
SERVICE_NAME="job-hunting-ai-backend"

echo ""
echo "Configuration:"
echo "  Project ID: $PROJECT_ID"
echo "  Region: $REGION"
echo "  Service Name: $SERVICE_NAME"
echo ""

# Set the gcloud project
echo "Setting gcloud project..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo ""
echo "Enabling required Google Cloud APIs..."
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    containerregistry.googleapis.com

# Ask for environment variables
echo ""
echo "================================================"
echo "Environment Variables Configuration"
echo "================================================"
read -p "Enter your ADZUNA_APP_ID: " ADZUNA_APP_ID
read -p "Enter your ADZUNA_APP_KEY: " ADZUNA_APP_KEY
read -p "Enter your SECRET_KEY (or press Enter to generate): " SECRET_KEY

if [ -z "$SECRET_KEY" ]; then
    SECRET_KEY=$(openssl rand -hex 32)
    echo "Generated SECRET_KEY: $SECRET_KEY"
fi

# Build and deploy using Cloud Build
echo ""
echo "Building and deploying to Cloud Run..."
echo "This may take several minutes..."

gcloud builds submit --config cloudbuild.yaml

# Set secret environment variables
echo ""
echo "Setting environment variables..."
gcloud run services update $SERVICE_NAME \
    --region=$REGION \
    --update-env-vars ADZUNA_APP_ID=$ADZUNA_APP_ID,ADZUNA_APP_KEY=$ADZUNA_APP_KEY,SECRET_KEY=$SECRET_KEY,USE_MOCK=0

# Allow public access
echo ""
echo "Setting public access policy..."
gcloud run services add-iam-policy-binding $SERVICE_NAME \
    --region=$REGION \
    --member=allUsers \
    --role=roles/run.invoker

echo ""
echo "================================================"
echo "Deployment Complete!"
echo "================================================"

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)')

echo ""
echo "Your application is now deployed at:"
echo "$SERVICE_URL"
echo ""
echo "Test the health endpoint:"
echo "curl $SERVICE_URL/health"
echo ""
