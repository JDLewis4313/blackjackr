import pytest
from flask import session
from app import create_app
from domains.game.routes import BlackjackGame


@pytest.fixture
def app():
    app = create_app(testing=True)
    app.config.update(
        SECRET_KEY='test',
        TESTING=True,
        WTF_CSRF_ENABLED=False,
        LOGIN_DISABLED=True
    )
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def fake_game_dict():
    game = BlackjackGame()
    return game.to_dict()


def test_play_route(client, app, fake_game_dict):
    with client.session_transaction() as sess:
        sess['game'] = fake_game_dict

    response = client.get('/game/play')
    assert response.status_code == 200
    assert b'player_hand' in response.data or b'dealer_hand' in response.data


def test_start_game(client):
    response = client.post('/game/start')
    assert response.status_code == 200
    data = response.get_json()
    assert 'player_hand' in data
    assert 'dealer_hand' in data
    assert isinstance(data['player_hand'], list)
    assert len(data['player_hand']) == 2


def test_hit_route(client):
    # Start a game first
    client.post('/game/start')
    response = client.post('/game/hit')
    assert response.status_code == 200
    data = response.get_json()
    assert 'player_hand' in data
    assert len(data['player_hand']) >= 2  # could be 3+ after a hit


def test_stand_route(client):
    # Start a game first
    client.post('/game/start')
    response = client.post('/game/stand')
    assert response.status_code == 200
    data = response.get_json()
    assert data['game_over'] is True
    assert data['result'] is not None
