from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Roles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50), unique=True, nullable=False)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    salt = db.Column(db.String(32), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))


class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    price = db.Column(db.Float)
    qr_code_id = db.Column(db.Integer, db.ForeignKey('qr_code.id'))


class QRCodes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())


class FailedClassifications(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.String(100), nullable=False)
    reason = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=db.func.now())


class Metadata(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), nullable=False, unique=True)
    value = db.Column(db.String(255), nullable=False)

