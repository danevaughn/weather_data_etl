from collections import defaultdict
from google.cloud import bigquery
from src.pipeline import bq
from src.pipeline import extract
from src.pipeline import load
from src.pipeline import transform
from unittest import mock

import json
import pandas as pd
import pandas.api.types as ptypes
import pytest



class TestBQ:

    def test_schema(self):
        assert type(bq.schema) == list
        assert all(isinstance(x, bigquery.SchemaField) for x in bq.schema)

    def test_get_columns(self):
        output = bq.get_columns(bq.schema)
        assert type(output) == list
        assert len(output) == len(bq.schema)
        assert all(isinstance(x, str) for x in output)

    def test_load_job_config(self):
        assert isinstance(bq.load_job_config, bigquery.LoadJobConfig)
        assert bq.load_job_config.write_disposition == 'WRITE_APPEND'
        assert bq.load_job_config.schema == bq.schema



class TestExtract:

    @pytest.fixture
    @mock.patch('src.pipeline.extract.storage.Client')
    def extractor(self, client):
        client.get_bucket.return_value.blob.return_value.download_as_bytes.return_value = b'"data"'
        extractor = extract.Extract(client)
        return extractor

    def test_get_storage_object(self, extractor):
        output = extractor._get_storage_object('bucket', 'blob')
        assert output == b'"data"'

    def test_get_decoded_blob(self, extractor):
        output = extractor.get_decoded_blob('bucket', 'blob')
        assert output == 'data'

    @pytest.mark.parametrize(
        'input,expected',
        [
            ('["data"]'.encode('utf-8'), ['data']),
            ('{"data": None}'.encode('utf-8'), {'data': None}),
            ('{"data": ["text", 1, [0]]}'.encode('utf-8'), {'data': ['text', 1, [0]]})
        ]
    )
    def test_decode_data(self, input, expected):
        output = extract.decode_data(input)
        assert output == expected



class TestLoad:

    @pytest.fixture
    @mock.patch('src.pipeline.load.bigquery.Client')
    def loader(self, client):
        client.load_table_from_dataframe.return_value.result.return_value = {'status': 1}
        config_mock = mock.Mock()
        config_mock.schema = 1
        config_mock.write_disposition = 'WRITE_APPEND'
        config_mock.ignore_unkown_values = True
        loader = load.Load(client, config_mock)
        return loader

    def test_insert_dataframe(self, loader):
        output = loader.insert_dataframe('data', 'table')
        assert output == {'status': 1}



class TestTransform:

    @pytest.fixture
    def transformer(self):
        with open('test_data.json') as test_data:
            json_data = json.loads(test_data.read())
            transformer = transform.Transform(json_data)
        return transformer

    @pytest.mark.parametrize(
        'input,expected',
        [
            (
                {'data': 1},
                {'data': [1]}
            ),
            (
                [{'data': [{'test': 1}]}],
                {'data_test': [1]}
            ),
            (
                {'data': 'test', 'id': 1},
                {'data': ['test'], 'id': [1]}
            ),
            (
                [{'data': 'test'}, {'id': 1}],
                {'data': ['test'], 'id': [1]}
            )
        ]
    )
    def test_flatten_dict(self, input, expected):
        output = transform.flatten_dict(input)
        assert type(output) is defaultdict
        assert output == expected

    def test_transform_temp_to_celsius(self, transformer):
        transformer.transform_temp_to_celsius()
        assert 'temp_unit' in transformer.dataframe.columns
        assert type(transformer.dataframe) is pd.DataFrame
        assert transformer.dataframe['main_temp'][0] == 726.85

    def test_transform_units(self, transformer):
        transformer.transform_units()
        assert type(transformer.dataframe) is pd.DataFrame
        assert transformer.dataframe['main_humidity'][0] == 10
        assert transformer.dataframe['wind_speed'][0] == 3600

    def test_add_event_columns(self, transformer):
        transformer.add_event_columns(bucket='bucket', blob='blob', creation_time='2022-01-01T00:00:00.0Z')
        cols_added = ['bucket_name', 'blob_name', 'timestamp', 'real_insert_timestamp']
        for col in cols_added:
            assert col in transformer.dataframe.columns
        assert ptypes.is_datetime64_any_dtype(transformer.dataframe['timestamp'])
        assert ptypes.is_datetime64_any_dtype(transformer.dataframe['real_insert_timestamp'])

    def test_apply(self, transformer):
        transformer.apply(bucket='bucket', blob='blob', creation_time='2022-01-01T00:00:00.0Z')
        col_num = len(bq.schema)
        assert col_num == len(transformer.dataframe.columns)