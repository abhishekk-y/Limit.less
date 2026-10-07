from app.runtime import apify_jobs

API = '/api/v1'

def test_apify_actor_input_and_import_are_real_and_private(test_client, register, monkeypatch):
    headers, _ = register()
    async def token(*args): return 'not-a-real-token'
    async def provider(secret, method, path, **kwargs):
        assert secret == 'not-a-real-token'
        if method == 'POST':
            assert path == '/acts/PeTP8M7vkdTthJvqk/runs'
            assert kwargs['json']['jobsToFetch'] == 10
            assert kwargs['json']['query'] == 'Python Developer'
            assert kwargs['params']['maxTotalChargeUsd'] == .5
            return {'data': {'id': 'run12345', 'defaultDatasetId': 'dataset123', 'status': 'READY'}}
        return [{'title': 'Python Developer', 'jobUrl': 'https://www.linkedin.com/jobs/view/123', 'companyName': 'Example', 'description': 'Python SQL'}]
    monkeypatch.setattr(apify_jobs, 'token', token)
    monkeypatch.setattr(apify_jobs, 'provider_call', provider)
    response = test_client.post(API + '/live-jobs/apify/search', headers=headers, json={'query':'Python Developer','location':'Berlin, Germany','limit':10,'approved':True})
    assert response.status_code == 202, response.text
    for _ in range(2):
        assert test_client.post(API + '/live-jobs/apify/import-dataset', headers=headers, json={'dataset_id':'dataset123'}).status_code == 200
    jobs = test_client.get(API + '/live-jobs', headers=headers).json()
    assert len(jobs) == 1 and jobs[0]['is_demo'] is False
    assert test_client.get(API + '/applications', headers=headers).json() == []
    stranger, _ = register('apify-other@example.com')
    assert test_client.get(API + '/live-jobs/apify/runs', headers=stranger).json() == []

def test_sas_workspace_and_hackathon_mode_do_not_create_applications(test_client, register):
    headers, _ = register()
    assert test_client.put(API + '/sas/workspace', headers=headers, json={'url':'m'}).status_code == 422
    saved = test_client.put(API + '/sas/workspace', headers=headers, json={'url':'https://vle.sas.com/vfl'})
    assert saved.status_code == 200 and saved.json()['execution_verified'] is False
    test_client.put(API + '/data/preferences', headers=headers, json={'source':'hackathon'})
    assert test_client.get(API + '/data/preferences', headers=headers).json()['source'] == 'hackathon'
    assert test_client.get(API + '/applications', headers=headers).json() == []
    assert test_client.get(API + '/live-jobs', headers=headers).json() == []
    assert test_client.get(API + '/sas-evidence/snapshot', headers=headers).json()['vfl_verification'] == 'pending'
