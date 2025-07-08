from . import db

class Language(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), unique=True, nullable=False)
    name = db.Column(db.String(64), nullable=False)

    def __repr__(self):
        return f"<Language {self.code}>"

class Currency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), unique=True, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    symbol = db.Column(db.String(8))

    def __repr__(self):
        return f"<Currency {self.code}>"

class UnitOfMeasurement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    abbreviation = db.Column(db.String(16), unique=True, nullable=False)

    def __repr__(self):
        return f"<UnitOfMeasurement {self.abbreviation}>"

