from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

db = SQLAlchemy()


class Roles(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50), unique=True, nullable=False)

    users = relationship('Users', back_populates='roles', lazy=True)


class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    salt = db.Column(db.String(32), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)

    roles = relationship('Roles', back_populates='users')


class Products(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    shelf = db.Column(db.Integer, nullable=False)
    price_piece = db.Column(db.Float)
    price_kg = db.Column(db.Float)
    qr_code_id = db.Column(db.Integer, db.ForeignKey('qr_codes.id'))

    qr_codes = relationship('QRCodes', back_populates='products')


class QRCodes(db.Model):
    __tablename__ = 'qr_codes'
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())

    products = relationship('Products', back_populates='qr_codes', lazy=True)


class FailedClassifications(db.Model):
    __tablename__ = 'failed_classifications'
    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.String(100), nullable=False)
    reason = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=db.func.now())


class Metadata(db.Model):
    __tablename__ = 'metadatas'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), nullable=False, unique=True)
    value = db.Column(db.String(255), nullable=False)
