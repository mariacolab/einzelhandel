import pytest
from ..app import create_db_session
from ..models import db


@pytest.fixture(scope="module")
def test_client():
    app = create_db_session()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://postgres:password@postgres:5432/microservices_db"

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client


# Test Routes
def test_add_role(test_client):
    response = test_client.post('/roles', json={'role_name': 'Admin'})
    assert response.status_code == 201
    assert response.json['role_name'] == 'Admin'

def test_get_role(test_client):
    response = test_client.get('/roles/1')
    assert response.status_code == 200
    assert response.json['role_name'] == 'Admin'

def test_update_role(test_client):
    response = test_client.put('/roles/1', json={'role_name': 'Super Admin'})
    assert response.status_code == 200
    assert response.json['role_name'] == 'Super Admin'

def test_delete_role(test_client):
    response = test_client.delete('/roles/1')
    assert response.status_code == 200
    assert response.json['status'] == 'Role deleted'


