import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '', '')))

from config import config

# config.update({'PROJECT_DIR': os.path.dirname(__file__) + '/'})
config.update({'TESTING': True})

from backend import create_app


@pytest.fixture
def client():
    """Charge l'objet et le renvoie"""
    app = create_app(config)
    with app.test_client() as client:
        yield client


def test_load_initial_data(client):
    """Vérifie que l'objet chargé n'est pas None"""
    #Given
    expected_response = None
    test_config = config
    test_config.update({'PROJECT_DIR': os.path.dirname(__file__) + '/'})
    test_config.update({'TESTING': True})
    app = create_app(test_config)
    #When
    actual_response = client.get('/load_initial_data/v2')

    #Then
    json_response = actual_response.json

    assert actual_response is not None # Vérifie si l'objet est None
    assert actual_response.status_code == 200
    assert json_response.get('ids') is not None


def test_load_data(client):
    """Vérifie que l'objet chargé n'est pas None"""
    #Given
    id = 100001
    expected_response = None
    #When
    actual_response = client.get('/load_data/v2/' + str(id))

    #Then
    json_response = actual_response.json

    assert actual_response is not None # Vérifie si l'objet est None
    assert actual_response.status_code == 200
    assert json_response.get('ids') is not None

def test_predict(client):
    """Vérifie que l'objet chargé n'est pas None"""
    #Given
    id = 100001

    expected_response = None
    #When
    response = client.get('/load_data/v2/' + str(id))
    actual_response = client.get('/load_data/v2/' + str(id))
    # json_response = response.json

    #Then
    json_response = actual_response.json

    assert actual_response is not None # Vérifie si l'objet est None
    assert actual_response.status_code == 200
    assert json_response.get('ids') is not None
