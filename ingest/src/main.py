from configparser import ConfigParser
from datetime import datetime
from google.cloud import storage
from gcloud_logger import gcloud_logger
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

import json
import requests
import os
import sys
import time

logger = gcloud_logger(__name__)
config = ConfigParser()
config.read(os.path.join(sys.path[0], 'config.cfg'))

KEY = config['OPENWEATHER']['Key']
MAX_RETRIES = int(config['DEFAULT']['MAX_RETRIES'])
BUCKET_NAME = config['GCLOUD']['Bucket']
BLOB_NAME = f'warsaw_weather_{datetime.now().strftime("%d_%m_%Y_%H_%M")}'
URL = f'https://api.openweathermap.org/data/2.5/weather?q=Warsaw&appid={KEY}'


def requests_retry_session(
    retries=MAX_RETRIES,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 503, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def get_data_and_save_in_memory(url) -> str:
    response = requests_retry_session().get(url).json()
    return json.dumps(response)


def upload_blob_to_gcs(bucket_name: str, data: str, destination_blob: str):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob)
    blob.upload_from_string(
        data=data,
        content_type='application/json')
    logger.info(f'Source file uploaded correctly to {bucket_name} as {destination_blob}.')


def main():
    data = get_data_and_save_in_memory(URL)
    upload_blob_to_gcs(BUCKET_NAME, data, BLOB_NAME)


if __name__=='__main__':
    main()
