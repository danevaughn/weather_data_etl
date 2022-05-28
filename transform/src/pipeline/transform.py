from collections import defaultdict
from typing import Dict, Any
from . import bq

import pandas as pd


def flatten_dict(data: dict) -> Dict[str, list]:
    output = defaultdict(list)
    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '_')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name)
                i += 1
        else:
            output[name[:-1]].append(x)
    flatten(data)
    return output


class Transform:

    def __init__(self, data: Dict[str, Any]):
        self.dataframe = pd.DataFrame(flatten_dict(data))

    def transform_temp_to_celsius(self) -> None:
        for column in self.dataframe:
            if 'temp' in column or column == 'main_feels_like':
                self.dataframe[column] -= 273.15
        self.dataframe['temp_unit'] = 'Celsius'


    def transform_units(self) -> None:
        self.dataframe['main_humidity'] /= 100
        self.dataframe['wind_speed'] *= 3.6


    def add_event_columns(self, bucket: str, blob: str, creation_time: str) -> None:
        self.dataframe['bucket_name'] = bucket
        self.dataframe['blob_name'] = blob
        self.dataframe['timestamp'] = creation_time
        self.dataframe['timestamp'] =  pd.to_datetime(self.dataframe['timestamp'], format='%Y-%m-%dT%H:%M:%S.%fZ')
        self.dataframe['real_insert_timestamp'] = pd.Timestamp.now()


    def apply(self, bucket: str, blob: str, creation_time: str) -> pd.DataFrame:
        self.transform_temp_to_celsius()
        self.transform_units()
        self.add_event_columns(
            bucket=bucket, blob=blob, creation_time=creation_time
            )
        columns_to_save = bq.get_columns()
        self.dataframe = self.dataframe[columns_to_save]
        return self.dataframe