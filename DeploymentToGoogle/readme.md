## carionic-e1f2d




gcloud run deploy hello-service \
  --image gcr.io/carionic-e1f2d/fastapi-hello \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 5001


gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  containerregistry.googleapis.com

# in bash
PROJECT_ID=carionic-e1f2d
IMAGE_NAME=fastapi-hello

gcloud builds submit --tag gcr.io/carionic-e1f2d/fastapi-hello

# service url
curl https://hello-service-585117608984.us-central1.run.app/hello

 