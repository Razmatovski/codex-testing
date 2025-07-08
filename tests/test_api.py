
def test_send_calculation_invalid_email(client):
    resp = client.post('/api/v1/send-calculation', json={
        'user_email': 'invalid',
        'language_code': 'en',
        'calculation_items': [{'quantity': '1', 'price_per_unit': '1', 'item_total_price': '1'}],
        'grand_total_price': '1'
    })
    assert resp.status_code == 400


def test_send_calculation_success(client):
    resp = client.post('/api/v1/send-calculation', json={
        'user_email': 'user@example.com',
        'language_code': 'en',
        'calculation_items': [{'quantity': '1', 'price_per_unit': '2', 'item_total_price': '2'}],
        'grand_total_price': '2'
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['status'] == 'success'
