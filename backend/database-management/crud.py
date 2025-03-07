"""
   von Maria Schuster
   Crud Methoden der Postgresql
"""
import base64
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from models import Roles, Users, Products, QRCodes, FailedClassifications, Metadata

def execute_query(session: Session, query, params=None):
    if params is None:
        params = {}
    result = session.execute(query, params)
    session.commit()
    return result


# Nutzerrolen CRUD
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


def read_role_by_name(session: Session, role_name: str):
    return session.query(Roles).filter_by(role_name=role_name).first()


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


# Benutzer CRUD
def create_user(session: Session, username: str, password: str, salt: str, role_id: int):
    try:
        users = Users(username=username, password=password, salt=salt, role_id=role_id)
        session.add(users)
        session.commit()
        return users
    except IntegrityError:
        session.rollback()
        return None


def read_user_by_id(session: Session, user_id: int):
    return session.query(Users).filter_by(id=user_id).first()


def read_user_by_name(session: Session, username: str):
    return session.query(Users).filter_by(username=username).first()


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


# Produkt CRUD
def create_product(session: Session, name: str, description: str, shelf: int,
                   price_piece: float, price_kg: float, qr_code_id: int):
    try:
        shelf = "" if shelf == 6 else shelf
        price_piece = None if price_piece == 1.99 else float(price_piece)
        price_kg = None if price_kg == 4.00 else float(price_kg)
        products = Products(name=name, description=description, shelf=shelf,
                            price_piece=price_piece, price_kg=price_kg, qr_code_id=qr_code_id)
        session.add(products)
        session.commit()
        return products
    except IntegrityError:
        session.rollback()
        return None


def create_product_without_qr(session: Session, name: str, description: str, shelf: int,
                              price_piece: float, price_kg: float):
    try:
        shelf = "" if shelf == 6 else shelf
        price_piece = None if price_piece == 1.99 else float(price_piece)
        price_kg = None if price_kg == 4.00 else float(price_kg)
        products = Products(name=name, description=description, shelf=shelf,
                            price_piece=price_piece, price_kg=price_kg)
        session.add(products)
        session.commit()
        return products
    except IntegrityError:
        session.rollback()
        return None


def read_products_by_name(session: Session, name: str):
    return session.query(Products).filter_by(name=name).first()


def read_product(session: Session, product_id: int):
    return session.query(Products).filter_by(id=product_id).first()


def update_product(session: Session, product_id: int, **updates):
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


# QR-Code CRUD
def create_qrcode(session: Session, image_blob: bytes):
    try:
        qrcodes = QRCodes(data=image_blob)
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
    failedclassifications = FailedClassifications(imageid=image_id, reason=reason)
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
