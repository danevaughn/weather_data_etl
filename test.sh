if [ gcloud iam roles describe weather_etl_user3213 --project=modular-visitor-350414 ]
then
    echo "role exists"
else
    echo "role not exists"
fi
