from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from . import db


class Language(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), unique=True, nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False)

    def __repr__(self):
        return f"<Language {self.code}>"


class Currency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), unique=True, nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False)
    symbol = db.Column(db.String(8))

    def __repr__(self):
        return f"<Currency {self.code}>"


class UnitOfMeasurement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    abbreviation = db.Column(
        db.String(16), unique=True, nullable=False, index=True
    )

    def __repr__(self):
        return f"<UnitOfMeasurement {self.abbreviation}>"


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False, index=True)

    def __repr__(self):
        return f"<Category {self.name}>"


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship(
        'Category',
        backref=db.backref('services', lazy=True),
    )
    unit_id = db.Column(db.Integer, db.ForeignKey('unit_of_measurement.id'))
    unit = db.relationship('UnitOfMeasurement')

    def __repr__(self):
        return f"<Service {self.name}>"


class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), unique=True, nullable=False)
    value = db.Column(db.String(256))

    def __repr__(self):
        return f"<Setting {self.key}>"


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"
