from flask import Flask, redirect, render_template, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)

db = SQLAlchemy()
login_manager = LoginManager()

from .forms import (
    LoginForm,
    UnitForm,
    CategoryForm,
    ServiceForm,
    SettingForm,
)
from .models import User, UnitOfMeasurement, Category, Service, Setting


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    from . import models  # noqa: F401
    from .api import api_bp

    app.register_blueprint(api_bp)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    register_routes(app)

    register_cli(app)

    return app


def register_cli(app: Flask) -> None:
    """Register custom Flask CLI commands."""

    @app.cli.command("init-db")
    def init_db_command():
        """Initialize database and create default data."""
        from .models import Language, Currency, UnitOfMeasurement

        tables = (
            db.engine.table_names()
            if hasattr(db.engine, "table_names")
            else db.inspect(db.engine).get_table_names()
        )
        if tables:
            confirm = input(
                "Existing tables detected. This will DELETE all data and recreate them. Continue? [y/N]: "
            )
            if confirm.lower() != "y":
                print("Aborted.")
                return
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

        admin = User(username="admin")
        admin.set_password("admin")

        db.session.add_all([en, ru, usd, eur, kg, pc, admin])
        db.session.commit()
        print("Database initialized")


def ensure_db_initialized(app: Flask) -> None:
    """Create database tables and default data if none exist."""
    from .models import Language, Currency, UnitOfMeasurement

    with app.app_context():
        tables = (
            db.engine.table_names()
            if hasattr(db.engine, "table_names")
            else db.inspect(db.engine).get_table_names()
        )
        if not tables:
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

            admin = User(username="admin")
            admin.set_password("admin")

            db.session.add_all([en, ru, usd, eur, kg, pc, admin])
            db.session.commit()


def register_routes(app: Flask) -> None:
    """Register web routes."""

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('units'))

        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and user.check_password(form.password.data):
                login_user(user)
                return redirect(url_for('units'))
            flash('Invalid credentials')
        return render_template('login.html', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))

    @app.route('/')
    def index():
        return redirect(url_for('units'))

    # Unit routes
    @app.route('/units', methods=['GET', 'POST'])
    @login_required
    def units():
        form = UnitForm()
        if form.validate_on_submit():
            unit = UnitOfMeasurement(name=form.name.data, abbreviation=form.abbreviation.data)
            db.session.add(unit)
            db.session.commit()
            return redirect(url_for('units'))
        units = UnitOfMeasurement.query.all()
        return render_template('units.html', form=form, units=units)

    @app.route('/units/edit/<int:unit_id>', methods=['GET', 'POST'])
    @login_required
    def edit_unit(unit_id):
        unit = UnitOfMeasurement.query.get_or_404(unit_id)
        form = UnitForm(obj=unit)
        if form.validate_on_submit():
            form.populate_obj(unit)
            db.session.commit()
            return redirect(url_for('units'))
        return render_template('units.html', form=form, units=UnitOfMeasurement.query.all())

    @app.route('/units/delete/<int:unit_id>')
    @login_required
    def delete_unit(unit_id):
        unit = UnitOfMeasurement.query.get_or_404(unit_id)
        db.session.delete(unit)
        db.session.commit()
        return redirect(url_for('units'))

    # Category routes
    @app.route('/categories', methods=['GET', 'POST'])
    @login_required
    def categories():
        form = CategoryForm()
        if form.validate_on_submit():
            category = Category(name=form.name.data)
            db.session.add(category)
            db.session.commit()
            return redirect(url_for('categories'))
        categories = Category.query.all()
        return render_template('categories.html', form=form, categories=categories)

    @app.route('/categories/edit/<int:category_id>', methods=['GET', 'POST'])
    @login_required
    def edit_category(category_id):
        category = Category.query.get_or_404(category_id)
        form = CategoryForm(obj=category)
        if form.validate_on_submit():
            form.populate_obj(category)
            db.session.commit()
            return redirect(url_for('categories'))
        return render_template('categories.html', form=form, categories=Category.query.all())

    @app.route('/categories/delete/<int:category_id>')
    @login_required
    def delete_category(category_id):
        category = Category.query.get_or_404(category_id)
        db.session.delete(category)
        db.session.commit()
        return redirect(url_for('categories'))

    # Service routes
    @app.route('/services', methods=['GET', 'POST'])
    @login_required
    def services():
        form = ServiceForm()
        form.category.choices = [(c.id, c.name) for c in Category.query.all()]
        form.unit.choices = [(u.id, u.abbreviation) for u in UnitOfMeasurement.query.all()]
        if form.validate_on_submit():
            service = Service(name=form.name.data, price=form.price.data,
                              category_id=form.category.data or None,
                              unit_id=form.unit.data or None)
            db.session.add(service)
            db.session.commit()
            return redirect(url_for('services'))
        services = Service.query.all()
        return render_template('services.html', form=form, services=services)

    @app.route('/services/edit/<int:service_id>', methods=['GET', 'POST'])
    @login_required
    def edit_service(service_id):
        service = Service.query.get_or_404(service_id)
        form = ServiceForm(obj=service)
        form.category.choices = [(c.id, c.name) for c in Category.query.all()]
        form.unit.choices = [(u.id, u.abbreviation) for u in UnitOfMeasurement.query.all()]
        if form.validate_on_submit():
            service.name = form.name.data
            service.price = form.price.data
            service.category_id = form.category.data or None
            service.unit_id = form.unit.data or None
            db.session.commit()
            return redirect(url_for('services'))
        return render_template('services.html', form=form, services=Service.query.all())

    @app.route('/services/delete/<int:service_id>')
    @login_required
    def delete_service(service_id):
        service = Service.query.get_or_404(service_id)
        db.session.delete(service)
        db.session.commit()
        return redirect(url_for('services'))

    # Setting routes
    @app.route('/settings', methods=['GET', 'POST'])
    @login_required
    def settings():
        form = SettingForm()
        if form.validate_on_submit():
            setting = Setting(key=form.key.data, value=form.value.data)
            db.session.add(setting)
            db.session.commit()
            return redirect(url_for('settings'))
        settings = Setting.query.all()
        return render_template('settings.html', form=form, settings=settings)

    @app.route('/settings/edit/<int:setting_id>', methods=['GET', 'POST'])
    @login_required
    def edit_setting(setting_id):
        setting = Setting.query.get_or_404(setting_id)
        form = SettingForm(obj=setting)
        if form.validate_on_submit():
            form.populate_obj(setting)
            db.session.commit()
            return redirect(url_for('settings'))
        return render_template('settings.html', form=form, settings=Setting.query.all())

    @app.route('/settings/delete/<int:setting_id>')
    @login_required
    def delete_setting(setting_id):
        setting = Setting.query.get_or_404(setting_id)
        db.session.delete(setting)
        db.session.commit()
        return redirect(url_for('settings'))




