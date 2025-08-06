import pytest
from flask import session
from domains.player.models import Player
from infrastructure.database.db import db


@pytest.fixture
def new_user_data():
    return {
        'name': 'Raviroyashe',
        'email': 'raviroyashe@gmail.com',
        'password': 'password@123'
    }


def test_register_success(client, new_user_data):
    response = client.post('/player/register', data=new_user_data, follow_redirects=True)
    assert response.status_code == 200
    user = Player.query.filter_by(email=new_user_data['email']).first()
    assert user is not None
    assert user.name == new_user_data['name']


def test_register_existing_email(client, new_user_data):
    # First registration
    client.post('/player/register', data=new_user_data)
    # Try again with the same email
    response = client.post('/player/register', data=new_user_data, follow_redirects=True)
    assert b"Email already registered." in response.data


def test_login_success(client, new_user_data):
    # First, register the user
    client.post('/player/register', data=new_user_data)
    login_data = {
        'email': new_user_data['email'],
        'password': new_user_data['password']
    }
    response = client.post('/player/login', data=login_data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Invalid credentials." not in response.data


def test_login_invalid_password(client, new_user_data):
    client.post('/player/register', data=new_user_data)
    response = client.post('/player/login', data={
        'email': new_user_data['email'],
        'password': 'wrongpassword'
    }, follow_redirects=True)
    assert b"Invalid credentials." in response.data


def test_logout(client, new_user_data):
    # Register and log in
    client.post('/player/register', data=new_user_data)
    response = client.get('/player/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b"Login" in response.data
