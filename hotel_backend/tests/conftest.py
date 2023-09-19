"""
pytest
- set environments | PYTHONPATH=project | BASIC_AUTH_USERNAME, BASIC_AUTH_PASSWORD
- run command with : pytest [directory_to_conftest.py] -vv -o log_cli=true
"""

import logging

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from mongomock import MongoClient
from server.main import app

LOGGER = logging.getLogger(__name__)
X_API_TOKEN = 'secret'
auth = {
    'username': 'dev',
    'password': 'secret',
    'scope': 'me, supervisor'
}
payload = {
    'username': 'dev',
    'firstname': 'watcharapon',
    'lastname': 'weeraborirak'
}


@pytest.fixture
def mock_mongo_client():
    # tear up or setup
    # Create a mock MongoDB client using mongomock
    db = MongoClient()
    yield db
    # tear down
    # Cleanup after all tests are executed
    db.close()


@pytest.fixture
def client(mock_mongo_client):
    # Use the TestClient with the FastAPI app
    return TestClient(app)


@pytest.fixture
def authorization_header(client):
    response = client.post('/auth/token', json=auth)
    return response.json()


def test_find_order(client, authorization_header):
    # tear up
    response = client.post('/order/find?skip=0&limit=10', json=payload,
                           headers={'Authorization': f'Bearer {authorization_header}', 'x-api-token': 'secret'})
    return response.status_code == status.HTTP_200_OK
