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
# password is "mudcake"
as_mary = {"headers":{"Authorization": "Basic bWFyeTptdWRjYWtl"}}

@pytest.fixture
def client():
    return testing.TestClient(api)

def test_admin_user_created_by_default(client):
    response = client.simulate_get(routes['users'], **as_admin)
    assert response.status == falcon.HTTP_OK
    body = json.loads(response.content, encoding='utf-8')
    validate(body, schemas.get_user)
    # There should be only 1 user in the system, and that user is 'admin'
    assert len(body['items']) == 1
    assert body['items'][0]['username'] == "admin"

def test_create_user(client):
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

@pytest.mark.dependency(depends=["test_create_user"])
def test_user_cannot_be_created_twice(client):
    response = create_user(client)
    assert response.status == falcon.HTTP_BAD_REQUEST

def test_unauthenticated_user_cannot_list_all_users(client):
    response = client.simulate_get(routes['users'])
    assert response.status == falcon.HTTP_UNAUTHORIZED

@pytest.mark.dependency(depends=["test_create_user"])
def test_retrieve_profile_by_username(client):
    response = client.simulate_get(routes['user'].format(username_or_id="bob"), **as_bob)
    assert response.status == falcon.HTTP_OK
    body = json.loads(response.content, encoding='utf-8')
    validate(body, schemas.get_user)
    assert len(body['items']) == 1
    assert body['items'][0]['username'] == "bob"

@pytest.mark.dependency(depends=["test_create_user"])
def test_retrieve_profile_by_id(client):
    # FRAGILE! This test assumes that there are only two users in the system,
    # 'admin' and 'bob' with id's 1 and 2. These id values are automatically
    # assigned by peewee and could be different it future releases (although unlikely).
    response = client.simulate_get(routes['user'].format(username_or_id=2), **as_bob)
    assert response.status == falcon.HTTP_OK
    body = json.loads(response.content, encoding='utf-8')
    validate(body, schemas.get_user)
    assert len(body['items']) == 1
    assert body['items'][0]['username'] == "bob"

a_book = {
    "title": "On Liberty",
    "author": "John Stuart Mill"
}

@pytest.mark.dependency(depends=["test_create_user"])
def test_add_book(client):
    response = client.simulate_post(routes['books'], body=json.dumps(a_book), **as_bob)
    assert response.status == falcon.HTTP_CREATED
    # FRAGILE! See the commend about user id values above.
    assert response.headers['location'] == routes['book'].format(id=1)

@pytest.mark.dependency(depends=["test_add_book"])
def test_individual_user_profile_lists_books(client):
    response = client.simulate_get(routes['user'].format(username_or_id="bob"), **as_bob)
    assert response.status == falcon.HTTP_OK
    body = json.loads(response.content, encoding='utf-8')
    # FRAGILE! See the commend about user id values above.
    assert body['items'][0]['books'][0] == "http://falconframework.org/v1/books/1"

def test_must_authenticate_to_list_books(client):
    response = client.simulate_get(routes['books'])
    assert response.status == falcon.HTTP_UNAUTHORIZED

@pytest.mark.dependency(depends=["test_add_book"])
def test_list_individual_book(client):
    response = client.simulate_get(routes['book'].format(id=1), **as_bob)
    assert response.status == falcon.HTTP_OK
    body = json.loads(response.content, encoding='utf-8')
    validate(body, schemas.get_book)

a_loan = {
    "book_id": 1,            # Loan Bob's copy of "On Liberty"
    "user_id": 1,            # to "admin"
    "date_due": "2019-02-14" # until Valentine's day
}

@pytest.mark.dependency(depends=["test_add_book"])
def test_add_loan(client):
    response = client.simulate_post(routes['loans'], body=json.dumps(a_loan), **as_bob)
    assert response.status == falcon.HTTP_CREATED

@pytest.mark.dependency(depends=["test_add_loan"])
def test_admin_can_list_all_loans(client):
    response = client.simulate_get(routes['loans'], **as_admin)
    assert response.status == falcon.HTTP_OK
    body = json.loads(response.content, encoding='utf-8')
    validate(body, schemas.get_loan)

bad_book_loan = {
    "book_id": 2,            # This book doesn't exist
    "user_id": 1,
    "date_due": "2019-03-01"
}

@pytest.mark.dependency(depends=["test_add_book"])
def test_cant_loan_book_that_does_not_exist(client):
    response = client.simulate_post(routes['loans'], body=json.dumps(bad_book_loan), **as_bob)
    assert response.status == falcon.HTTP_NOT_FOUND

bad_user_loan = {
    "book_id": 1,
    "user_id": 3,            # This user doesn't exist
    "date_due": "2019-03-01"
}

@pytest.mark.dependency(depends=["test_add_book"])
def test_cant_loan_book_to_user_that_does_not_exist(client):
    response = client.simulate_post(routes['loans'], body=json.dumps(bad_user_loan), **as_bob)
    assert response.status == falcon.HTTP_NOT_FOUND

loan_to_mary = {
    "book_id": 1,            # This book is owned by Bob
    "user_id": 2,
    "date_due": "2019-03-31"
}

@pytest.mark.dependency(depends=["test_add_book"])
def test_cannot_loan_book_you_do_not_own(client):
    response = create_user(client, "mary", "mudcake")
    assert response.status == falcon.HTTP_CREATED
    # Mary should not be allowed to loan Bob's book to herself
    response = client.simulate_post(routes['loans'], body=json.dumps(loan_to_mary), **as_mary)
    assert response.status == falcon.HTTP_UNAUTHORIZED
