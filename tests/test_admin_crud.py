from admin_app import db
from admin_app.models import (
    UnitOfMeasurement,
    Category,
    Service,
    Setting,
    Language,
    Currency,
)


def login(client):
    return client.post(
        '/login',
        data={'username': 'admin', 'password': 'admin'},
        follow_redirects=True,
    )


def test_unit_crud(client, app):
    login(client)
    client.post(
        '/units',
        data={'name': 'Kilogram', 'abbreviation': 'kg'},
        follow_redirects=True,
    )
    with app.app_context():
        unit = UnitOfMeasurement.query.filter_by(abbreviation='kg').first()
        assert unit is not None
    client.post(
        f'/units/edit/{unit.id}',
        data={'name': 'Gram', 'abbreviation': 'g'},
        follow_redirects=True,
    )
    with app.app_context():
        unit = db.session.get(UnitOfMeasurement, unit.id)
        assert unit.name == 'Gram'
        assert unit.abbreviation == 'g'
    client.get(f'/units/delete/{unit.id}', follow_redirects=True)
    with app.app_context():
        assert db.session.get(UnitOfMeasurement, unit.id) is None


def test_category_crud(client, app):
    login(client)
    client.post('/categories', data={'name': 'New Cat'}, follow_redirects=True)
    with app.app_context():
        cat = Category.query.filter_by(name='New Cat').first()
        assert cat is not None
    client.post(
        f'/categories/edit/{cat.id}',
        data={'name': 'Updated Cat'},
        follow_redirects=True,
    )
    with app.app_context():
        cat = db.session.get(Category, cat.id)
        assert cat.name == 'Updated Cat'
    client.get(f'/categories/delete/{cat.id}', follow_redirects=True)
    with app.app_context():
        assert db.session.get(Category, cat.id) is None


def test_delete_multiple_categories(client, app):
    login(client)
    names = ['A', 'B', 'C']
    for n in names:
        client.post('/categories', data={'name': n}, follow_redirects=True)
    with app.app_context():
        ids = [str(c.id) for c in Category.query.filter(Category.name.in_(names)).all()]
    client.post('/categories/delete-selected', data={'category_ids': ids}, follow_redirects=True)
    with app.app_context():
        for cid in ids:
            assert db.session.get(Category, int(cid)) is None


def test_delete_multiple_units(client, app):
    login(client)
    data = [
        ('Gram', 'g'),
        ('Kilogram', 'kg'),
        ('Meter', 'm'),
    ]
    for name, abbr in data:
        client.post(
            '/units',
            data={'name': name, 'abbreviation': abbr},
            follow_redirects=True,
        )
    with app.app_context():
        ids = [
            str(u.id)
            for u in UnitOfMeasurement.query.filter(
                UnitOfMeasurement.abbreviation.in_([d[1] for d in data])
            ).all()
        ]
    client.post(
        '/units/delete-selected',
        data={'unit_ids': ids},
        follow_redirects=True,
    )
    with app.app_context():
        for uid in ids:
            assert db.session.get(UnitOfMeasurement, int(uid)) is None


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
        svc = db.session.get(Service, svc.id)
        assert svc.name == 'Svc2'
        assert svc.price == 10
    client.get(f'/services/delete/{svc.id}', follow_redirects=True)
    with app.app_context():
        assert db.session.get(Service, svc.id) is None


def test_update_default_settings(client, app):
    login(client)
    with app.app_context():
        lang = Language.query.first()
        cur = Currency.query.first()

    client.post(
        '/settings',
        data={'language': str(lang.id), 'currency': str(cur.id)},
        follow_redirects=True,
    )

    with app.app_context():
        lang_setting = Setting.query.filter_by(
            key='default_language_id'
        ).first()
        cur_setting = Setting.query.filter_by(
            key='default_currency_id'
        ).first()
        assert lang_setting.value == str(lang.id)
        assert cur_setting.value == str(cur.id)
