#bin/bash

set -e

if [ $# -ne 3 ] ; then
	echo "Enter your project, bucket name and region as ./set_up_infra.sh <project-name> <bucket-name> <region>"
	exit 0
fi

PROJECT_ID=$1
BUCKET_NAME=$2
REGION=$3

# Authorize user
gcloud auth login

# Set project
gcloud config set project $PROJECT_ID

# Enable services
gcloud services enable logging.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable bigquery.googleapis.com

# Create service account and add permissions
gcloud iam service-accounts create weather-app-service-account \
	--description="Service account for interacting with Google Cloud services for weather data ETL purposes" \
	--display-name="weather-app-service-account" \

gcloud projects add-iam-policy-binding $PROJECT_ID \
	--member="serviceAccount:weather-app-service-account@$PROJECT_ID.iam.gserviceaccount.com" \
	--role="roles/logging.bucketWriter"

gcloud projects add-iam-policy-binding $PROJECT_ID \
	--member="serviceAccount:weather-app-service-account@$PROJECT_ID.iam.gserviceaccount.com" \
	--role="roles/logging.logWriter"

gcloud projects add-iam-policy-binding $PROJECT_ID \
	--member="serviceAccount:weather-app-service-account@$PROJECT_ID.iam.gserviceaccount.com" \
	--role="roles/storage.objectCreator"

gcloud projects add-iam-policy-binding $PROJECT_ID \
	--member="serviceAccount:weather-app-service-account@$PROJECT_ID.iam.gserviceaccount.com" \
	--role="roles/storage.objectViewer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
	--member="serviceAccount:weather-app-service-account@$PROJECT_ID.iam.gserviceaccount.com" \
	--role="roles/bigquery.jobUser"

gcloud projects add-iam-policy-binding $PROJECT_ID \
	--member="serviceAccount:weather-app-service-account@$PROJECT_ID.iam.gserviceaccount.com" \
	--role="roles/bigquery.dataEditor"

# Generate service account's private key and save it locally so Docker can access it
gcloud iam service-accounts keys create $(pwd)/ingest/google_cloud_credentials.json \
	--iam-account="weather-app-service-account@$PROJECT_ID.iam.gserviceaccount.com"

# Create bucket for storing raw data and add permission
gsutil mb \
	-c STANDARD \
	-l $REGION \
	gs://$BUCKET_NAME

gsutil acl ch -u weather-app-service-account@$PROJECT_ID.iam.gserviceaccount.com:R \
	gs://${BUCKET_NAME}

# Create Pub/Sub topic for given bucket
gsutil notification create -t weather_app_topic -f json gs://$BUCKET_NAME

# Create BQ dataset
bq --location=$REGION mk \
--dataset \
--description="Raw Warsaw weather data" \
$PROJECT_ID:weather_data

# Deploy Cloud Function
gcloud functions deploy transform_weather_data \
	--region=$REGION \
	--runtime=python39 \
	--entry-point=main \
	--trigger-topic=weather_app_topic \
	--memory=256 \
	--retry \
	--source=./transform/src/ \
	--update-env-vars=TABLE=weather_data.raw_weather_data

# Ask user if provided configs to Docker, if yes then start container
while true; do
    read -p "Have you passed the data in the configuration file (./ingest/src/config.cfg)? [y/n]" yn
    case $yn in
        [Yy]* ) cd ./ingest && docker-compose up; break;;
        [Nn]* ) exit;;
        * ) echo "Please answer yes or no.";;
    esac
done