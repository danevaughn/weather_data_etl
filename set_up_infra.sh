#!bin/bash

set -e

if [[ $# -ne 3 ]] ; then
	echo "Enter your project, bucket name and region as ./set_up_infra.sh <project-name> <bucket-name> <region>"
	exit 0
fi

PROJECT_ID=$1
BUCKET_NAME=$2
REGION=$3

PERMISSIONS=logging.logEntries.create,logging.buckets.write,storage.objects.get,storage.objects.create,bigquery.jobs.create,bigquery.datasets.create,bigquery.tables.create

# Authorize user
gcloud auth login

# Set project
gcloud config set project $PROJECT_ID

# Check if billing is enabled
if gcloud beta billing projects describe $PROJECT_ID | grep "billingEnabled: false"; then
	echo "Billing does not seem to be enabled for project $PROJECT_ID. Enable it first."
	exit 0
fi

# Enable services
echo "Enabling services..."
gcloud services enable logging.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable bigquery.googleapis.com
echo "Done"

# Create service account
echo "Creating service account weather_app_service_account..."
gcloud iam service-accounts create weather-app-service-account \
	--description="Service account for interacting with Google Cloud services for weather data ETL purposes" \
	--display-name="weather-app-service-account" \
	--no-user-output-enabled
echo "Done"

# Create custom role
echo "Creating custom role weather_etl_user..."
if ! gcloud iam roles describe weather_etl_user --project=$PROJECT_ID; then
	gcloud iam roles create weather_etl_user \
		--project=$PROJECT_ID \
		--permissions=$PERMISSIONS \
		--no-user-output-enabled
fi
echo "Done"

# Assign role to service account
echo "Adding custom role weather_etl_user to service account weather_app_service_account..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
	--member="serviceAccount:weather-app-service-account@$PROJECT_ID.iam.gserviceaccount.com" \
	--role="projects/$PROJECT_ID/roles/weather_etl_user" \
	--no-user-output-enabled
echo "Done"

# Generate service account's private key and save it locally so Docker can access it
echo "Generating service account's private key and saving it locally..."
gcloud iam service-accounts keys create $(pwd)/ingest/google_cloud_credentials.json \
	--iam-account="weather-app-service-account@$PROJECT_ID.iam.gserviceaccount.com" \
	--no-user-output-enabled
echo "Done"

# Create bucket for storing raw data and add permission
gsutil mb \
	-c STANDARD \
	-l $REGION \
	gs://$BUCKET_NAME
echo "Done"

echo "Adding required permissions for bucket $BUCKET_NAME..."
gsutil acl ch -u weather-app-service-account@$PROJECT_ID.iam.gserviceaccount.com:R \
	gs://${BUCKET_NAME}

# Create Pub/Sub topic for given bucket
echo "Creating Pub/Sub topic weather_app_topic for bucket $BUCKET_NAME..."
gsutil notification create -t weather_app_topic -f json gs://$BUCKET_NAME

# Create BQ dataset
echo "Creating BigQuery dataset $PROJECT_ID:weather_data in region $REGION..."
bq --location=$REGION mk \
	--dataset \
	--description="Raw Warsaw weather data" \
	$PROJECT_ID:weather_data

# Deploy Cloud Function
echo "Deploying transform_weather_data function in region $REGION... (may take couple minutes)"
gcloud functions deploy transform_weather_data \
	--region=$REGION \
	--runtime=python39 \
	--entry-point=main \
	--trigger-topic=weather_app_topic \
	--memory=256 \
	--retry \
	--source=./transform/src/ \
	--update-env-vars=TABLE=weather_data.raw_weather_data \
	--no-user-output-enabled
echo "Done"

# Ask user if provided configs to Docker, if yes then start container
while true; do
    read -p "Have you passed the data in the configuration file (./ingest/src/config.cfg)? [y/n]" yn
    case $yn in
        [Yy]* ) cd ./ingest && docker-compose up; break;;
        [Nn]* ) exit;;
        * ) echo "Please answer yes or no.";;
    esac
done

