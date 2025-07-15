
def test_calculator_data_endpoint(client):
    resp = client.get('/api/v1/calculator-data')
    assert resp.status_code == 200
    data = resp.get_json()
    assert set(data.keys()) == {
        'settings',
        'languages',
        'currencies',
        'units_of_measurement',
        'categories',
    }
    assert isinstance(data['settings'], dict)
    assert 'default_currency_id' in data['settings']
    assert 'default_language_id' in data['settings']
    assert isinstance(data['languages'], list)
    assert any(lang['id'] == 'uk' for lang in data['languages'])
    assert isinstance(data['currencies'], list)
    assert isinstance(data['units_of_measurement'], list)
    assert isinstance(data['categories'], list)
