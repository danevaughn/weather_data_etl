from google.cloud import bigquery, storage
from pipeline import bq
from pipeline.extract import Extract
from pipeline.load import Load
from pipeline.transform import Transform
from utils.exceptions import FailedBigQueryJob, NoDataException

import base64
import json
import os


PROJECT_ID = os.environ.get('GCP_PROJECT')
BQ_TABLE = os.environ.get('TABLE')
BQ_CLIENT = bigquery.Client()
STORAGE_CLIENT = storage.Client()


def main(event, context) -> None:
    if 'data' in event:
        event_data = json.loads(base64.b64decode(event['data']).decode('utf-8'))
    else:
        raise NoDataException

    bucket = event_data['bucket']
    blob = event_data['name']
    creation_time = event_data['timeCreated']

    extract = Extract(STORAGE_CLIENT)
    extracted_data = extract.get_decoded_blob(bucket=bucket, blob=blob)

    transform = Transform(extracted_data)
    transformed_data = transform.apply(
        blob=blob, bucket=bucket, creation_time=creation_time
        )
    
    load = Load(BQ_CLIENT, job_config=bq.load_job_config)
    result = load.insert_dataframe(transformed_data, BQ_TABLE)
    if result.errors:
        raise FailedBigQueryJob(result.errors)


if __name__=='__main__':
    main()
