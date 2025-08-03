from io import StringIO
from collections import namedtuple

from admin_app.utils.io import export_csv, import_csv


def test_export_csv_basic():
    Item = namedtuple('Item', ['id', 'name'])
    items = [Item(1, 'a'), Item(2, 'b')]
    data = export_csv(items, [
        ('id', lambda o: o.id),
        ('name', lambda o: o.name),
    ])
    assert data.strip().splitlines() == ['id,name', '1,a', '2,b']


def test_import_csv_validators_and_upsert():
    csv_data = 'a,b\n1,2\n3,x\n'
    stream = StringIO(csv_data)

    def validator(fields):
        required = {'a', 'b'}
        if not fields or not required.issubset(fields):
            return 'missing'

    rows = []

    def upsert(row, line_num):
        if not row['b'].isdigit():
            return f'Row {line_num}: b must be int'
        rows.append((row['a'], int(row['b'])))

    errors = import_csv(stream, [validator], upsert)
    assert errors == ['Row 3: b must be int']
    assert rows == [('1', 2)]


def test_import_csv_missing_columns():
    stream = StringIO('a\n1\n')

    def validator(fields):
        required = {'a', 'b'}
        if not fields or not required.issubset(fields):
            return 'missing'

    errors = import_csv(stream, [validator], lambda row, ln: None)
    assert errors == ['missing']
