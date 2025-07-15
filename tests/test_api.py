import smtplib


class DummySMTP:
    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        pass

    def starttls(self):
        pass

    def login(self, user, password):
        pass

    def send_message(self, message):
        self.sent = True


def test_send_calculation_invalid_email(client):
    resp = client.post(
        '/api/v1/send-calculation',
        json={
            'user_email': 'invalid',
            'language_code': 'en',
            'calculation_items': [
                {
                    'quantity': '1',
                    'price_per_unit': '1',
                    'item_total_price': '1',
                }
            ],
            'grand_total_price': '1',
        },
    )
    assert resp.status_code == 400


def test_send_calculation_success(client, monkeypatch):
    monkeypatch.setattr(smtplib, 'SMTP', lambda *a, **kw: DummySMTP())
    resp = client.post(
        '/api/v1/send-calculation',
        json={
            'user_email': 'user@example.com',
            'language_code': 'en',
            'calculation_items': [
                {
                    'quantity': '1',
                    'price_per_unit': '2',
                    'item_total_price': '2',
                }
            ],
            'grand_total_price': '2',
        },
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['status'] == 'success'


class FailingSMTP(DummySMTP):
    def send_message(self, message):
        raise smtplib.SMTPException('fail')


def test_send_calculation_smtp_error(client, monkeypatch):
    monkeypatch.setattr(smtplib, 'SMTP', lambda *a, **kw: FailingSMTP())
    resp = client.post(
        '/api/v1/send-calculation',
        json={
            'user_email': 'user@example.com',
            'language_code': 'en',
            'calculation_items': [
                {
                    'quantity': '1',
                    'price_per_unit': '2',
                    'item_total_price': '2',
                }
            ],
            'grand_total_price': '2',
        },
    )
    assert resp.status_code == 500
    data = resp.get_json()
    assert data['status'] == 'error'
