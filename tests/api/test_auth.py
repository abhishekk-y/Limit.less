def test_real_login_and_duplicate_registration(test_client, register):
    headers, data = register()
    assert data['user']['role'] == 'professional'
    login = test_client.post('/api/v1/auth/login', json={'email': 'learner@example.com', 'password': 'Secure-pass-12345'})
    assert login.status_code == 200
    assert login.json()['access_token'] != data['access_token']
    duplicate = test_client.post('/api/v1/auth/register', json={'email': 'learner@example.com', 'name': 'Duplicate', 'password': 'Secure-pass-12345', 'consent': True})
    assert duplicate.status_code == 409
    assert test_client.get('/api/v1/auth/me', headers=headers).status_code == 200
