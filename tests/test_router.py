import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_user():
    new_user = {
        'username': 'Finn',
        'email': 'adventuretime@yandex.ru',
        'password': 'gfdsaqz'
    }
    response = client.post('/api/users/', json=new_user)
    assert response.status_code == 200