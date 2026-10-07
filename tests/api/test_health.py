def test_real_health_endpoint(test_client):
    response = test_client.get('/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'
    assert response.json()['version'] == '0.2.0'
    assert response.headers['x-content-type-options'] == 'nosniff'
