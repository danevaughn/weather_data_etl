import requests
import pytest

from src.main import requests_retry_session
from src.main import get_data_and_save_in_memory
from src.main import upload_blob_to_gcs

from unittest import mock
from unittest.mock import Mock


class TestRequests:
    def test_requests_retry_session_redirects(self):
        response = requests_retry_session(retries=2).get('https://httpbin.org/redirect/:n')
        assert response.status_code == 404
    
    def test_requests_retry_session_code_200(self):
        response = requests_retry_session(retries=2).get("https://postman-echo.com/status/200")
        assert response.status_code == 200

    def test_requests_retry_session_url_not_existing(self):
        with pytest.raises(requests.exceptions.ConnectionError):
            requests_retry_session(retries=2).get("http://this-url-does-not.exist")

    def test_requests_retry_sesion_code_500(self):
        with pytest.raises(requests.exceptions.RetryError):
            requests_retry_session(retries=2).get("https://postman-echo.com/status/500")

    def test_requests_retry_sesion_code_502(self):
        with pytest.raises(requests.exceptions.RetryError):
            requests_retry_session(retries=2).get("https://postman-echo.com/status/502")

    def test_requests_retry_sesion_code_503(self):
        with pytest.raises(requests.exceptions.RetryError):
            requests_retry_session(retries=2).get("https://postman-echo.com/status/503")

    def test_requests_retry_sesion_code_504(self):
        with pytest.raises(requests.exceptions.RetryError):
            requests_retry_session(retries=2).get("https://postman-echo.com/status/504")


class TestMain:
    @mock.patch('src.main.requests_retry_session')
    def test_get_data_and_save_in_memory(self, mock_requests):
        mock_response = Mock()
        mock_requests.return_value.get.return_value = mock_response
        mock_response.json.return_value = [{'test': 1}]
        output = get_data_and_save_in_memory('test.url')
        mock_response.json.assert_called_once()
        assert output == '[{"test": 1}]'
            
    
    @mock.patch('src.main.storage')
    def test_upload_blob_to_gcs(self, mock_storage):
        mock_gcs_client = mock_storage.Client.return_value
        mock_bucket = Mock()
        mock_gcs_client.bucket.return_value = mock_bucket
        upload_blob_to_gcs('test_bucket', 'test_data', 'test_blob')
        mock_storage.Client.assert_called_once()
        mock_gcs_client.bucket.assert_called_once_with('test_bucket')
        mock_bucket.blob.assert_called_once_with('test_blob')
        mock_bucket.blob.return_value.upload_from_string.assert_called_once()