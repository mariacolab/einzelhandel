from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from models import Roles, Users, Products, QRCodes, FailedClassifications, Metadata


# General Utility for Prepared Queries
def execute_query(session: Session, query, params=None):
    if params is None:
        params = {}
    result = session.execute(query, params)
    session.commit()
    return result


# Role CRUD
def create_role(session: Session, role_name: str):
    try:
        roles = Roles(role_name=role_name)
        session.add(roles)
        session.commit()
        return roles
    except IntegrityError:
        session.rollback()
        return None


def read_role(session: Session, role_id: int):
    return session.query(Roles).filter_by(id=role_id).first()


def update_role(session: Session, role_id: int, new_role_name: str):
    roles = session.query(Roles).filter_by(id=role_id).first()
    if roles:
        roles.role_name = new_role_name
        session.commit()
    return roles


def delete_role(session: Session, role_id: int):
    roles = session.query(Roles).filter_by(id=role_id).first()
    if roles:
        session.delete(roles)
        session.commit()
    return roles


# User CRUD
def create_user(session: Session, username: str, password: str, salt: str, role_id: int):
    try:
        users = Users(username=username, password=password, salt=salt, role_id=role_id)
        session.add(users)
        session.commit()
        return users
    except IntegrityError:
        session.rollback()
        return None


def read_user(session: Session, user_id: int):
    return session.query(Users).filter_by(id=user_id).first()


def update_user(session: Session, user_id: int, updates: dict):
    users = session.query(Users).filter_by(id=user_id).first()
    if users:
        for key, value in updates.items():
            setattr(users, key, value)
        session.commit()
    return users


def delete_user(session: Session, user_id: int):
    users = session.query(Users).filter_by(id=user_id).first()
    if users:
        session.delete(users)
        session.commit()
    return users


# Product CRUD
def create_product(session: Session, name: str, description: str, price: float, qr_code_id: int):
    try:
        products = Products(name=name, description=description, price=price, qr_code_id=qr_code_id)
        session.add(products)
        session.commit()
        return products
    except IntegrityError:
        session.rollback()
        return None


def read_product(session: Session, product_id: int):
    return session.query(Products).filter_by(id=product_id).first()


def update_product(session: Session, product_id: int, updates: dict):
    products = session.query(Products).filter_by(id=product_id).first()
    if products:
        for key, value in updates.items():
            setattr(products, key, value)
        session.commit()
    return products


def delete_product(session: Session, product_id: int):
    products = session.query(Products).filter_by(id=product_id).first()
    if products:
        session.delete(products)
        session.commit()
    return products


# QRCode CRUD
def create_qrcode(session: Session, data: str):
    try:
        qrcodes = QRCodes(data=data)
        session.add(qrcodes)
        session.commit()
        return qrcodes
    except IntegrityError:
        session.rollback()
        return None


def read_qrcode(session: Session, qr_code_id: int):
    return session.query(QRCodes).filter_by(id=qr_code_id).first()


def delete_qrcode(session: Session, qr_code_id: int):
    qrcodes = session.query(QRCodes).filter_by(id=qr_code_id).first()
    if qrcodes:
        session.delete(qrcodes)
        session.commit()
    return qrcodes


# FailedClassification CRUD
def create_failed_classification(session: Session, image_id: str, reason: str):
    failedclassifications = FailedClassifications(image_id=image_id, reason=reason)
    session.add(failedclassifications)
    session.commit()
    return failedclassifications


def read_failed_classifications(session: Session):
    return session.query(FailedClassifications).all()


def delete_failed_classification(session: Session, classification_id: int):
    failedclassifications = session.query(FailedClassifications).filter_by(id=classification_id).first()
    if failedclassifications:
        session.delete(failedclassifications)
        session.commit()
    return failedclassifications


# Metadata CRUD
def create_metadata(session: Session, key: str, value: str):
    try:
        metadata = Metadata(key=key, value=value)
        session.add(metadata)
        session.commit()
        return metadata
    except IntegrityError:
        session.rollback()
        return None


def read_metadata(session: Session, key: str):
    return session.query(Metadata).filter_by(key=key).first()


def update_metadata(session: Session, key: str, value: str):
    metadata = session.query(Metadata).filter_by(key=key).first()
    if metadata:
        metadata.value = value
        session.commit()
    return metadata


def delete_metadata(session: Session, key: str):
    metadata = session.query(Metadata).filter_by(key=key).first()
    if metadata:
        session.delete(metadata)
        session.commit()
    return metadata

# General Utility for Prepared Queries
# def execute_query(session: Session, query, params=None):
#     if params is None:
#         params = {}
#     result = session.execute(query, params)
#     session.commit()
#     return result
#
#
# # Role CRUD
# def create_role(session: Session, role_name: str):
#     query = """
#     INSERT INTO roles (role_name)
#     VALUES (:role_name)
#     RETURNING *;
#     """
#     params = {"role_name": role_name}
#     try:
#         result = execute_query(session, query, params)
#         return result.fetchone()
#     except IntegrityError:
#         session.rollback()
#         return None
#
#
# def read_role(session: Session, role_id: int):
#     query = """
#     SELECT * FROM roles WHERE id = :role_id;
#     """
#     params = {"role_id": role_id}
#     result = execute_query(session, query, params)
#     return result.fetchone()
#
#
# def update_role(session: Session, role_id: int, new_role_name: str):
#     query = """
#     UPDATE roles
#     SET role_name = :new_role_name
#     WHERE id = :role_id
#     RETURNING *;
#     """
#     params = {"role_id": role_id, "new_role_name": new_role_name}
#     result = execute_query(session, query, params)
#     return result.fetchone()
#
#
# def delete_role(session: Session, role_id: int):
#     query = """
#     DELETE FROM roles
#     WHERE id = :role_id
#     RETURNING *;
#     """
#     params = {"role_id": role_id}
#     result = execute_query(session, query, params)
#     return result.fetchone()
#
#
# # User CRUD
# def create_user(session: Session, username: str, password: str, salt: str, role_id: int):
#     query = """
#     INSERT INTO users (username, password, salt, role_id)
#     VALUES (:username, :password, :salt, :role_id)
#     RETURNING *;
#     """
#     params = {"username": username, "password": password, "salt": salt, "role_id": role_id}
#     try:
#         result = execute_query(session, query, params)
#         return result.fetchone()
#     except IntegrityError:
#         session.rollback()
#         return None
#
#
# def read_user(session: Session, user_id: int):
#     query = """
#     SELECT * FROM users WHERE id = :user_id;
#     """
#     params = {"user_id": user_id}
#     result = execute_query(session, query, params)
#     return result.fetchone()
#
#
# def update_user(session: Session, user_id: int, updates: dict):
#     set_clause = ", ".join([f"{key} =: {key}" for key in updates.keys()])
#     query = f"""
#     UPDATE users
#     SET {set_clause}
#     WHERE id = :user_id
#     RETURNING *;
#     """
#     params = {"user_id": user_id, **updates}
#     result = execute_query(session, query, params)
#     return result.fetchone()
#
#
# def delete_user(session: Session, user_id: int):
#     query = """
#     DELETE FROM users
#     WHERE id = :user_id
#     RETURNING *;
#     """
#     params = {"user_id": user_id}
#     result = execute_query(session, query, params)
#     return result.fetchone()
#
#
# # Product CRUD
# def create_product(session: Session, name: str, description: str, price: float, qr_code_id: int):
#     query = """
#     INSERT INTO products (name, description, price, qr_code_id)
#     VALUES (:name, :description, :price, :qr_code_id)
#     RETURNING *;
#     """
#     params = {"name": name, "description": description, "price": price, "qr_code_id": qr_code_id}
#     try:
#         result = execute_query(session, query, params)
#         return result.fetchone()
#     except IntegrityError:
#         session.rollback()
#         return None
#
#
# def read_product(session: Session, product_id: int):
#     query = """
#     SELECT * FROM products WHERE id = :product_id;
#     """
#     params = {"product_id": product_id}
#     result = execute_query(session, query, params)
#     return result.fetchone()
#
#
# def update_product(session: Session, product_id: int, updates: dict):
#     set_clause = ", ".join([f"{key} =: {key}" for key in updates.keys()])
#     query = f"""
#     UPDATE products
#     SET {set_clause}
#     WHERE id = :product_id
#     RETURNING *;
#     """
#     params = {"product_id": product_id, **updates}
#     result = execute_query(session, query, params)
#     return result.fetchone()
#
#
# def delete_product(session: Session, product_id: int):
#     query = """
#     DELETE FROM products
#     WHERE id = :product_id
#     RETURNING *;
#     """
#     params = {"product_id": product_id}
#     result = execute_query(session, query, params)
#     return result.fetchone()
#
#
# # QRCode CRUD
# def create_qrcode(session: Session, data: str):
#     query = """
#     INSERT INTO qr_codes (data)
#     VALUES (:data)
#     RETURNING *;
#     """
#     params = {"data": data}
#     try:
#         result = execute_query(session, query, params)
#         return result.fetchone()
#     except IntegrityError:
#         session.rollback()
#         return None
#
#
# def read_qrcode(session: Session, qr_code_id: int):
#     query = """
#     SELECT * FROM qr_codes WHERE id = :qr_code_id;
#     """
#     params = {"qr_code_id": qr_code_id}
#     result = execute_query(session, query, params)
#     return result.fetchone()
#
#
# def delete_qrcode(session: Session, qr_code_id: int):
#     query = """
#     DELETE FROM qr_codes
#     WHERE id = :qr_code_id
#     RETURNING *;
#     """
#     params = {"qr_code_id": qr_code_id}
#     result = execute_query(session, query, params)
#     return result.fetchone()
#
#
# # FailedClassification CRUD
# def create_failed_classification(session: Session, image_id: str, reason: str):
#     query = """
#     INSERT INTO failed_classifications (image_id, reason)
#     VALUES (:image_id, :reason)
#     RETURNING *;
#     """
#     params = {"image_id": image_id, "reason": reason}
#     result = execute_query(session, query, params)
#     return result.fetchone()
#
#
# def read_failed_classifications(session: Session):
#     query = """
#     SELECT * FROM failed_classifications;
#     """
#     result = execute_query(session, query)
#     return result.fetchall()
#
#
# def delete_failed_classification(session: Session, classification_id: int):
#     query = """
#     DELETE FROM failed_classifications
#     WHERE id = :classification_id
#     RETURNING *;
#     """
#     params = {"classification_id": classification_id}
#     result = execute_query(session, query, params)
#     return result.fetchone()
#
#
# # Metadata CRUD
# def create_metadata(session: Session, key: str, value: str):
#     query = """
#     INSERT INTO metadata (key, value)
#     VALUES (:key, :value)
#     RETURNING *;
#     """
#     params = {"key": key, "value": value}
#     try:
#         result = execute_query(session, query, params)
#         return result.fetchone()
#     except IntegrityError:
#         session.rollback()
#         return None
#
#
# def read_metadata(session: Session, key: str):
#     query = """
#     SELECT * FROM metadata WHERE key = :key;
#     """
#     params = {"key": key}
#     result = execute_query(session, query, params)
#     return result.fetchone()
#
#
# def update_metadata(session: Session, key: str, value: str):
#     query = """
#     UPDATE metadata
#     SET value = :value
#     WHERE key = :key
#     RETURNING *;
#     """
#     params = {"key": key, "value": value}
#     result = execute_query(session, query, params)
#     return result.fetchone()
#
#
# def delete_metadata(session: Session, key: str):
#     query = """
#     DELETE FROM metadata
#     WHERE key = :key
#     RETURNING *;
#     """
#     params = {"key": key}
#     result = execute_query(session, query, params)
#     return result.fetchone()
