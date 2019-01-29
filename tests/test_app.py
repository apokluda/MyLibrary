import falcon
from falcon import testing

from unittest.mock import mock_open, call

import json
import pytest

from mylibrary.app import api

# Recursively sort lists and dictionaries of lists to enable comparing json
# documents. (https://stackoverflow.com/a/25851972)
def ordered(obj):
    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(ordered(x) for x in obj)
    else:
        return obj

@pytest.fixture
def client():
    return testing.TestClient(api)

# pytest will inject the object returned by the "client" function
# as an additional parameter.
def test_list_images(client):
    doc = {'users': None}

    response = client.simulate_get('/user')
    result_doc = json.loads(response.content, encoding='utf-8')

    assert ordered(result_doc) == ordered(doc)
    assert response.status == falcon.HTTP_OK

def test_new_user_gets_created(client, monkeypatch):
    new_user_json = '{"username":"joe"}';
    response = client.simulate_post('/user', body=new_user_json, headers={'content-type': 'application/json'})

    assert response.status == falcon.HTTP_CREATED
    assert response.headers['location'] == '/user/{}'.format("joe")
