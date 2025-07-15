from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
migrate = Migrate()
db = SQLAlchemy()
login_manager = LoginManager()

from .models import User  # noqa: E402


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'admin.login'

    from . import models  # noqa: F401
    from .api import api_bp
    from .routes import admin_bp

    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    register_cli(app)

    return app


def register_cli(app: Flask) -> None:
    """Register custom Flask CLI commands."""

    @app.cli.command("init-db")
    def init_db_command():
        """Initialize database and create default data."""
        from .models import Language, Currency, UnitOfMeasurement

        tables = db.inspect(db.engine).get_table_names()
        if tables:
            confirm = input(
                "Existing tables detected. "
                "This will DELETE all data and recreate them. "
                "Continue? [y/N]: "
            )
            if confirm.lower() != "y":
                print("Aborted.")
                return
            db.drop_all()

        db.create_all()

        # Default languages
        en = Language(code="en", name="English")
        ru = Language(code="ru", name="Russian")
        pl = Language(code="pl", name="Polish")
        uk = Language(code="uk", name="Ukrainian")

        # Default currencies
        usd = Currency(code="USD", name="US Dollar", symbol="$")
        eur = Currency(code="EUR", name="Euro", symbol="€")
        pln = Currency(code="PLN", name="Polish Zloty", symbol="zł")

        # Default units of measurement
        kg = UnitOfMeasurement(name="Kilogram", abbreviation="kg")
        pc = UnitOfMeasurement(name="Piece", abbreviation="pc")

        admin = User(username="admin")
        admin.set_password("admin")

        db.session.add_all([en, ru, pl, uk, usd, eur, pln, kg, pc, admin])
        db.session.commit()
        print("Database initialized")


def ensure_db_initialized(app: Flask) -> None:
    """Create database tables and default data if none exist."""
    from .models import Language, Currency, UnitOfMeasurement

    with app.app_context():
        tables = db.inspect(db.engine).get_table_names()
        if not tables:
            db.create_all()

            # Default languages
            en = Language(code="en", name="English")
            ru = Language(code="ru", name="Russian")
            pl = Language(code="pl", name="Polish")
            uk = Language(code="uk", name="Ukrainian")

            # Default currencies
            usd = Currency(code="USD", name="US Dollar", symbol="$")
            eur = Currency(code="EUR", name="Euro", symbol="€")
            pln = Currency(code="PLN", name="Polish Zloty", symbol="zł")

            # Default units of measurement
            kg = UnitOfMeasurement(name="Kilogram", abbreviation="kg")
            pc = UnitOfMeasurement(name="Piece", abbreviation="pc")

            admin = User(username="admin")
            admin.set_password("admin")

            db.session.add_all([en, ru, pl, uk, usd, eur, pln, kg, pc, admin])
            db.session.commit()
