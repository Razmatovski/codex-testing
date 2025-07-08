from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    db.init_app(app)

    from . import models  # noqa: F401

    register_cli(app)

    return app


def register_cli(app: Flask) -> None:
    """Register custom Flask CLI commands."""

    @app.cli.command("init-db")
    def init_db_command():
        """Initialize database and create default data."""
        from .models import Language, Currency, UnitOfMeasurement

        db.drop_all()
        db.create_all()

        # Default languages
        en = Language(code="en", name="English")
        ru = Language(code="ru", name="Russian")

        # Default currencies
        usd = Currency(code="USD", name="US Dollar", symbol="$")
        eur = Currency(code="EUR", name="Euro", symbol="€")

        # Default units of measurement
        kg = UnitOfMeasurement(name="Kilogram", abbreviation="kg")
        pc = UnitOfMeasurement(name="Piece", abbreviation="pc")

        db.session.add_all([en, ru, usd, eur, kg, pc])
        db.session.commit()
        print("Database initialized")


app = create_app()


