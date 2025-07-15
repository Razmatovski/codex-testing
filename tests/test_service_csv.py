import csv
from io import StringIO, BytesIO
from .test_admin_crud import login
from admin_app.models import Service, Category, UnitOfMeasurement


def test_export_services_csv(client, app):
    login(client)
    resp = client.get('/services/export')
    assert resp.status_code == 200
    data = resp.data.decode('utf-8')
    reader = csv.DictReader(StringIO(data))
    rows = list(reader)
    assert rows
    with app.app_context():
        names = {s.name for s in Service.query.all()}
    assert names == {row['name'] for row in rows}


def test_import_services_csv_success(client, app):
    login(client)
    with app.app_context():
        cat = Category.query.first()
        unit = UnitOfMeasurement.query.first()
    csv_data = (
        'name,price,category,unit\nNew,2,%s,%s\nTest Service,3,%s,%s\n'
        % (
            cat.name,
            unit.abbreviation,
            cat.name,
            unit.abbreviation,
        )
    )
    data = {
        'file': (BytesIO(csv_data.encode('utf-8')), 'services.csv'),
    }
    resp = client.post(
        '/services/import',
        data=data,
        content_type='multipart/form-data',
    )
    assert resp.status_code == 302
    with app.app_context():
        assert Service.query.filter_by(name='New').first() is not None
        svc = Service.query.filter_by(name='Test Service').first()
        assert svc.price == 3.0


def test_import_services_csv_creates_related(client, app):
    login(client)
    csv_data = 'name,price,category,unit\nBrand New,4,BrandCat,BC\n'
    data = {
        'file': (BytesIO(csv_data.encode('utf-8')), 'services.csv'),
    }
    resp = client.post(
        '/services/import',
        data=data,
        content_type='multipart/form-data',
    )
    assert resp.status_code == 302
    with app.app_context():
        cat = Category.query.filter_by(name='BrandCat').first()
        unit = UnitOfMeasurement.query.filter_by(abbreviation='BC').first()
        svc = Service.query.filter_by(name='Brand New').first()
        assert cat is not None
        assert unit is not None
        assert svc.category_id == cat.id
        assert svc.unit_id == unit.id


def test_import_services_csv_validation_error(client):
    login(client)
    bad_csv = 'wrong\n1,2,3\n'
    data = {'file': (BytesIO(bad_csv.encode('utf-8')), 'bad.csv')}
    resp = client.post(
        '/services/import',
        data=data,
        content_type='multipart/form-data',
    )
    assert resp.status_code == 400


def test_import_services_csv_trims_and_case_insensitive(client, app):
    login(client)
    csv_data = (
        'name,price,category,unit\n  test service ,2,  test category , PC \n'
    )
    data = {'file': (BytesIO(csv_data.encode('utf-8')), 'services.csv')}
    resp = client.post(
        '/services/import',
        data=data,
        content_type='multipart/form-data',
    )
    assert resp.status_code == 302
    with app.app_context():
        services = Service.query.filter_by(name='Test Service').all()
        assert len(services) == 1
        svc = services[0]
        assert svc.price == 2.0
        cat = Category.query.filter_by(name='Test Category').first()
        unit = UnitOfMeasurement.query.filter_by(abbreviation='pc').first()
        assert svc.category_id == cat.id
        assert svc.unit_id == unit.id


def test_import_services_csv_reuses_related_case_insensitive(client, app):
    login(client)
    csv_data = (
        'name,price,category,unit\nOther,5, TEST CATEGORY , Pc \n'
    )
    data = {'file': (BytesIO(csv_data.encode('utf-8')), 'services.csv')}
    resp = client.post(
        '/services/import',
        data=data,
        content_type='multipart/form-data',
    )
    assert resp.status_code == 302
    with app.app_context():
        svc = Service.query.filter_by(name='Other').first()
        assert svc is not None
        cat = Category.query.filter_by(name='Test Category').all()
        assert len(cat) == 1
        unit = UnitOfMeasurement.query.filter_by(abbreviation='pc').all()
        assert len(unit) == 1
        assert svc.category_id == cat[0].id
        assert svc.unit_id == unit[0].id
