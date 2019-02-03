import falcon
from falcon import testing

from unittest.mock import mock_open, call

import json
from jsonschema import validate
import pytest
import base64

from mylibrary.app import application as api
import mylibrary.schemas as schemas
import mylibrary.routes

routes = mylibrary.routes.routes

def create_user(client, username="bob", password="icecream"):
    return client.simulate_post(routes['users'],
        body=json.dumps({"username":username,"password":password}))

# password is "passw0rd"
as_admin = {"headers":{"Authorization":"Basic YWRtaW46cGFzc3cwcmQ="}}
# password is "icecream"
as_bob = {"headers":{"Authorization": "Basic Ym9iOmljZWNyZWFt"}}

@pytest.fixture
def client():
    return testing.TestClient(api)

def test_admin_user_created_by_default(client):
    response = client.simulate_get(routes['users'], **as_admin)
    assert response.status == falcon.HTTP_OK
    body = json.loads(response.content, encoding='utf-8')
    validate(body, schemas.get_user_schema)
    # There should be only 1 user in the system, and that user is 'admin'
    assert len(body['items']) == 1
    assert body['items'][0]['username'] == "admin"

def test_new_user_gets_created(client):
    response = create_user(client)
    assert response.status == falcon.HTTP_CREATED
    assert response.headers['location'] == routes['user'].format(username_or_id="bob")

def test_create_user_requires_password(client):
    response = client.simulate_post(routes['users'], body=json.dumps({"username":"foo"}))
    assert response.status == falcon.HTTP_BAD_REQUEST
    body = json.loads(response.content, encoding='utf-8')
    # FRAGILE! The description returned in the response body is generated
    # by jsonschema and could change in future releases
    assert body['description'] == "'password' is a required property"

def test_create_user_requires_username(client):
    response = client.simulate_post(routes['users'], body=json.dumps({"password":"barbaz"}))
    assert response.status == falcon.HTTP_BAD_REQUEST
    body = json.loads(response.content, encoding='utf-8')
    # FRAGILE! The description returned in the response body is generated
    # by jsonschema and could change in future releases
    assert body['description'] == "'username' is a required property"

def test_username_must_not_start_with_a_number(client):
    response = create_user(client, "2cool")
    assert response.status == falcon.HTTP_BAD_REQUEST
    body = json.loads(response.content, encoding='utf-8')
    # FRAGILE! The description returned in the response body is generated
    # by jsonschema and could change in future releases
    assert body['description'].startswith("'2cool' does not match") # '[pattern]'"

def test_password_must_not_be_too_short(client):
    response = create_user(client, "bob", "12345")
    assert response.status == falcon.HTTP_BAD_REQUEST
    body = json.loads(response.content, encoding='utf-8')
    # FRAGILE! The description returned in the response body is generated
    # by jsonschema and could change in future releases
    assert body['description'] == "'12345' is too short"

@pytest.mark.dependency(depends=["test_new_user_gets_created"])
def test_user_cannot_be_created_twice(client):
    response = create_user(client)
    assert response.status == falcon.HTTP_BAD_REQUEST

@pytest.mark.dependency(depends=["test_new_user_gets_created"])
def test_unpriviledged_user_cannot_list_all_users(client):
    response = client.simulate_get(routes['users'], **as_bob)
    assert response.status == falcon.HTTP_UNAUTHORIZED

def test_unauthenticated_user_cannot_list_all_users(client):
    response = client.simulate_get(routes['users'])
    assert response.status == falcon.HTTP_UNAUTHORIZED

@pytest.mark.dependency(depends=["test_new_user_gets_created"])
def test_user_can_retrieve_own_profile_by_username(client):
    response = client.simulate_get(routes['user'].format(username_or_id="bob"), **as_bob)
    assert response.status == falcon.HTTP_OK
    body = json.loads(response.content, encoding='utf-8')
    validate(body, schemas.get_user_schema)
    assert len(body['items']) == 1
    assert body['items'][0]['username'] == "bob"

@pytest.mark.dependency(depends=["test_new_user_gets_created"])
def test_user_can_retrieve_own_profile_by_id(client):
    # FRAGILE! This test assumes that there are only two users in the system,
    # 'admin' and 'bob' with id's 1 and 2. These id values are automatically
    # assigned by peewee and could be different it future releases (although unlikely).
    response = client.simulate_get(routes['user'].format(username_or_id=2), **as_bob)
    assert response.status == falcon.HTTP_OK
    body = json.loads(response.content, encoding='utf-8')
    validate(body, schemas.get_user_schema)
    assert len(body['items']) == 1
    assert body['items'][0]['username'] == "bob"

@pytest.mark.dependency(depends=["test_new_user_gets_created"])
def test_admin_can_retrieve_individual_user_by_username(client):
    response = client.simulate_get(routes['user'].format(username_or_id="bob"), **as_admin)
    assert response.status == falcon.HTTP_OK
    body = json.loads(response.content, encoding='utf-8')
    validate(body, schemas.get_user_schema)
    assert len(body['items']) == 1
    assert body['items'][0]['username'] == "bob"

@pytest.mark.dependency(depends=["test_new_user_gets_created"])
def test_admin_can_retrieve_individual_profile_by_id(client):
    # FRAGILE! See comment above.
    response = client.simulate_get(routes['user'].format(username_or_id=2), **as_admin)
    assert response.status == falcon.HTTP_OK
    body = json.loads(response.content, encoding='utf-8')
    validate(body, schemas.get_user_schema)
    assert len(body['items']) == 1
    assert body['items'][0]['username'] == "bob"
