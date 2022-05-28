from google.cloud import bigquery
from typing import Any

import pandas as pd


class Load:

    def __init__(self, bq_client: bigquery.Client) -> None:
        self.bq_client = bq_client

    def insert_dataframe(
        self, dataframe: pd.DataFrame, table_id: str, job_config: bigquery.LoadJobConfig
        ) -> Any:
        job = self.bq_client.load_table_from_dataframe(
            dataframe, table_id, num_retries=3, job_config=job_config
        )
        return job.result()