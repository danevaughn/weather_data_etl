import os
import sys
sys.path.append('/home/adrian/Desktop/weather_etl/transform')
from . import transform
import base64
import pytest
import storage


class TestExtract:
    
    @pytext.fixture()
    def storage_client(self):
        return storage.Client()

    def test_get_storage_object(self, client):
        expected = base64.b64encode('{"test": 1}')
        output = client._get_storage_object(bucket='test', blob='test')
        assert output
        assert output == expected
    
    def test_get_decoded_blob(self, client):
        expected = '{"test": 1}'
        output = client.get_decoded_blob(bucket='test', blob='test')
        assert output
        assert output == expected
        

class TestTransform:

    @pytest.fixture(autouse=True)
    def data():
        yield {''}

    def test_flatten_dict(self):
        expected = 1
        output = transform.flatten_dict()
        assert output == expected
        assert '' in output
        assert len(output) == 1

    @pytest.fixture(autouse=True)
    def dataframe(self, data):
        df = transform.Transform(data)
        yield df

    def test_transform_temp_to_celsius(self, dataframe):
        df = dataframe.transform_temp_to_celsius()
        assert 'temp_unit' in df.columns

    def test_transform_units(self, dataframe):
        pass

    def test_add_event_columns(self, dataframe):
        pass

    def test_apply(self, dataframe):
        pass