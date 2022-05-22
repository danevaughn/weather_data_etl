#bin/bash

set -e

if [ $# -ne 3 ] ; then
	echo "Enter your project and bucket name to delete as ./tear_down_infra.sh <project-name> <bucket-name>"
	exit 0
fi

echo "Starting infra clean up..."

PROJECT_ID=$1
BUCKET_NAME=$2
REGION=$3

# Stop docker container
cd ./ingest &&
docker-compose down &&
cd ..

# Authorize user
gcloud auth login

# Set project
gcloud config set project $PROJECT_ID

# Delete whole BigQuery dataset
bq rm -r -f \
    --quiet \
    --dataset $PROJECT_ID:weather_data \

# Delete Cloud Function resources
gcloud functions delete transform_weather_data \
    --region=$REGION \
    --quiet

# Delete Pub/Sub topic associated with Bucket
gcloud pubsub topics delete weather_app_topic \
    --quiet

# Delete bucket and it's content
gsutil rm -r gs://$BUCKET_NAME \

# Delete service account
gcloud iam service-accounts delete weather-app-service-account@$PROJECT_ID.iam.gserviceaccount.com \
    --quiet

# Delete the credentials file
rm ./ingest/google_cloud_credentials.json

echo "Clean up done"

