from configparser import ConfigParser
from datetime import datetime
from google.cloud import storage
from gcloud_logger import gcloud_logger
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from typing import Collection

import json
import requests
import os
import sys


def requests_retry_session(
    retries: int = 10,
    backoff_factor: float = 0.3,
    status_forcelist: Collection[int] = (500, 502, 503, 504),
    session: requests.Session = None,
) -> requests.Session:
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def get_data_and_save_in_memory(url: str) -> str:
    response = requests_retry_session().get(url).json()
    return json.dumps(response)


def upload_blob_to_gcs(bucket_name: str, data: str, destination_blob: str) -> None:
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob)
    blob.upload_from_string(
        data=data,
        content_type='application/json'
        )


def main() -> None:
    config = ConfigParser()
    config.read('config.cfg')
    logger = gcloud_logger(__name__)

    KEY = config['OPENWEATHER']['Key']
    MAX_RETRIES = int(config['DEFAULT']['MAX_RETRIES'])
    BUCKET_NAME = config['GCLOUD']['Bucket']
    BLOB_NAME = f'warsaw_weather_{datetime.now().strftime("%d_%m_%Y_%H_%M")}'
    URL = f'https://api.openweathermap.org/data/2.5/weather?q=Warsaw&appid={KEY}'

    data = get_data_and_save_in_memory(URL)
    upload_blob_to_gcs(BUCKET_NAME, data, BLOB_NAME)

    logger.info(f'Source file uploaded correctly to {BUCKET_NAME} as {BLOB_NAME}.')


if __name__=='__main__':
    main()
