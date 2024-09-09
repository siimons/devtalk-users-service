import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_delete_article():
    response = client.delete('/api/article/2')
    assert response.status_code == 200