from admin_app.models import (
    UnitOfMeasurement,
    Category,
    Service,
    Setting,
    Language,
    Currency,
)


def login(client):
    return client.post('/login', data={'username': 'admin', 'password': 'admin'}, follow_redirects=True)


def test_unit_crud(client, app):
    login(client)
    client.post('/units', data={'name': 'Kilogram', 'abbreviation': 'kg'}, follow_redirects=True)
    with app.app_context():
        unit = UnitOfMeasurement.query.filter_by(abbreviation='kg').first()
        assert unit is not None
    client.post(f'/units/edit/{unit.id}', data={'name': 'Gram', 'abbreviation': 'g'}, follow_redirects=True)
    with app.app_context():
        unit = UnitOfMeasurement.query.get(unit.id)
        assert unit.name == 'Gram'
        assert unit.abbreviation == 'g'
    client.get(f'/units/delete/{unit.id}', follow_redirects=True)
    with app.app_context():
        assert UnitOfMeasurement.query.get(unit.id) is None


def test_category_crud(client, app):
    login(client)
    client.post('/categories', data={'name': 'New Cat'}, follow_redirects=True)
    with app.app_context():
        cat = Category.query.filter_by(name='New Cat').first()
        assert cat is not None
    client.post(f'/categories/edit/{cat.id}', data={'name': 'Updated Cat'}, follow_redirects=True)
    with app.app_context():
        cat = Category.query.get(cat.id)
        assert cat.name == 'Updated Cat'
    client.get(f'/categories/delete/{cat.id}', follow_redirects=True)
    with app.app_context():
        assert Category.query.get(cat.id) is None


def test_service_crud(client, app):
    login(client)
    with app.app_context():
        category = Category.query.first()
        unit = UnitOfMeasurement.query.first()
    client.post('/services', data={
        'name': 'Svc',
        'price': '5',
        'category': str(category.id),
        'unit': str(unit.id)
    }, follow_redirects=True)
    with app.app_context():
        svc = Service.query.filter_by(name='Svc').first()
        assert svc is not None
    client.post(f'/services/edit/{svc.id}', data={
        'name': 'Svc2',
        'price': '10',
        'category': str(category.id),
        'unit': str(unit.id)
    }, follow_redirects=True)
    with app.app_context():
        svc = Service.query.get(svc.id)
        assert svc.name == 'Svc2'
        assert svc.price == 10
    client.get(f'/services/delete/{svc.id}', follow_redirects=True)
    with app.app_context():
        assert Service.query.get(svc.id) is None


def test_update_default_settings(client, app):
    login(client)
    with app.app_context():
        lang = Language.query.first()
        cur = Currency.query.first()

    client.post('/settings', data={'language': str(lang.id), 'currency': str(cur.id)}, follow_redirects=True)

    with app.app_context():
        lang_setting = Setting.query.filter_by(key='default_language_id').first()
        cur_setting = Setting.query.filter_by(key='default_currency_id').first()
        assert lang_setting.value == str(lang.id)
        assert cur_setting.value == str(cur.id)
