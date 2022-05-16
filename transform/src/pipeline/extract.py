from google.api_core import retry
from google.cloud import storage
from typing import Any, List, Dict, Union

import ast


def decode_data(data: bytes) -> List[Dict[str, Any]]:
    decoded_blob = data.decode('utf-8')
    decoded_data = ast.literal_eval(decoded_blob)
    return decoded_data


class Extract:

    def __init__(self, storage_client: storage.Client) -> None:
        self.client = storage_client

    @retry.Retry(initial=3.0, maximum=60.0, deadline=240.0)
    def _get_storage_object(self, bucket: str, blob: str) -> bytes:
        bucket_obj = self.client.get_bucket(bucket)
        blob_obj = bucket_obj.blob(blob)
        data = blob_obj.download_as_bytes(timeout=60)
        return data

    def get_decoded_blob(self, bucket: str, blob: str) -> Union[dict, list]:
        raw_blob = self._get_storage_object(bucket=bucket, blob=blob)
        decoded_blob = decode_data(raw_blob)
        return decoded_blob

