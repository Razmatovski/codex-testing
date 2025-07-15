import pytest
from admin_app import create_app, db
from admin_app.models import (
    Language,
    Currency,
    UnitOfMeasurement,
    Category,
    Service,
    Setting,
    User,
)


@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SMTP_SERVER'] = 'localhost'
    app.config['SMTP_PORT'] = 25
    with app.app_context():
        db.create_all()
        lang = Language(code='en', name='English')
        lang_uk = Language(code='uk', name='Ukrainian')
        currency = Currency(code='USD', name='US Dollar', symbol='$')
        unit = UnitOfMeasurement(name='Piece', abbreviation='pc')
        category = Category(name='Test Category')
        db.session.add_all([lang, lang_uk, currency, unit, category])
        db.session.commit()
        service = Service(name='Test Service', price=1.0,
                          category_id=category.id, unit_id=unit.id)
        setting1 = Setting(key='default_currency_id', value=currency.code)
        setting2 = Setting(key='default_language_id', value=lang.code)
        user = User(username='admin')
        user.set_password('admin')
        db.session.add_all([service, setting1, setting2, user])
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def login(client):
    def do_login():
        return client.post(
            '/login',
            data={'username': 'admin', 'password': 'admin'},
            follow_redirects=True,
        )

    return do_login
