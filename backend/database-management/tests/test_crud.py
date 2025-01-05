import pytest
from ..app import app
from ..models import db
from ..crud import (
    create_role, read_role, update_role, delete_role,
    create_user, read_user_by_id, update_user, delete_user,
    create_product, read_product, update_product, delete_product
)

def setup_database():
    with app.app_context():
        db.create_all()
        db.session.commit()

@pytest.fixture(scope="module")
def test_client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://postgres:password@postgres:5432/microservices_test"
    with app.app_context():
        db.init_app(app)
        setup_database()
        yield app.test_client()
        db.drop_all()


# Test CRUD Operations
def test_create_role():
    with app.app_context():
        role = create_role(db.session, role_name='Manager')
        assert role.role_name == 'Manager'

        read_role_data = read_role(db.session, role.id)
        assert read_role_data.role_name == 'Manager'

        updated_role = update_role(db.session, role.id, 'Team Lead')
        assert updated_role.role_name == 'Team Lead'

        delete_result = delete_role(db.session, role.id)
        assert delete_result is True

def test_user_crud():
    with app.app_context():
        user = create_user(db.session, username='testuser', password='password', salt='12345', role_id=None)
        assert user.username == 'testuser'

        read_user_data = read_user_by_id(db.session, user.id)
        assert read_user_data.username == 'testuser'

        updated_user = update_user(db.session, user.id, username='updateduser', password='newpassword', salt='67890', role_id=None)
        assert updated_user.username == 'updateduser'

        delete_result = delete_user(db.session, user.id)
        assert delete_result is True

def test_product_crud():
    with app.app_context():
        product = create_product(db.session, name='Laptop', description='A fast laptop', price=1200.00, qr_code_id=None)
        assert product.name == 'Laptop'

        read_product_data = read_product(db.session, product.id)
        assert read_product_data.name == 'Laptop'

        updated_product = update_product(db.session, product.id, name='Updated Laptop', description='Updated description', price=1300.00, qr_code_id=None)
        assert updated_product.name == 'Updated Laptop'

        delete_result = delete_product(db.session, product.id)
        assert delete_result is True
