from datetime import datetime as RealDateTime
from datetime import timedelta, timezone

API = '/api/v1'


def test_live_import_is_scoped_deduplicated_and_does_not_submit(test_client, register, monkeypatch):
    async def fake_board(board):
        return {'jobs': [{'id': 1, 'title': 'Python intern', 'location': {'name': 'Remote'},
            'content': '<p>Build Python and SQL applications</p>', 'absolute_url': 'https://boards.greenhouse.io/test/jobs/1'}]}
    monkeypatch.setattr('app.runtime.reach.fetch_board', fake_board)
    headers, _ = register()
    for _ in range(2):
        assert test_client.post(API + '/live-jobs/import', headers=headers, json={'board': 'test'}).json()['imported'] == 1
    jobs = test_client.get(API + '/live-jobs', headers=headers).json()
    assert len(jobs) == 1 and jobs[0]['is_demo'] is False
    assert jobs[0]['type'] == 'internship'
    insights = test_client.get(API + '/market-insights', headers=headers).json()
    assert insights['current']['active_postings'] == 1
    assert insights['current']['internship_postings'] == 1
    assert insights['current']['skill_counts'] == {'python': 1, 'sql': 1}
    assert insights['current']['skill_coverage_percent'] == 100
    assert insights['trend'] is None and insights['forecast'] is None
    assert insights['trend_status'] == 'collecting_history'
    roadmap = test_client.post(API + '/career-gps', headers=headers, json={'job_id': jobs[0]['id'], 'hours': 40})
    assert roadmap.status_code == 200, roadmap.text
    assert roadmap.json()['role']['title'] == 'Python intern · test'
    assert set(roadmap.json()['role']['skills']) == {'python', 'sql'}
    stranger, _ = register('reach-stranger@example.com')
    assert test_client.get(API + '/live-jobs', headers=stranger).json() == []
    assert test_client.post(API + '/apply-queue/prepare', headers=stranger, json={'job_ids': [jobs[0]['id']]}).status_code == 404
    body = {'job_ids': [jobs[0]['id']]}
    packet = test_client.post(API + '/apply-queue/prepare', headers=headers, json=body).json()[0]
    assert packet['submitted'] is False
    assert packet['status'] == 'ready_for_review'
    assert test_client.post(API + '/apply-queue/prepare', headers=headers, json=body).json()[0]['id'] == packet['id']
    assert test_client.post(API + '/apply-queue/' + packet['id'] + '/approve', headers=headers,
        json={'approved': True, 'version': 1}).status_code == 409
    assert test_client.post(API + '/apply-queue/' + packet['id'] + '/refresh', headers=headers).json()['version'] == 2
    async def empty_board(board): return {'jobs': []}
    monkeypatch.setattr('app.runtime.reach.fetch_board', empty_board)
    assert test_client.post(API + '/live-jobs/import', headers=headers, json={'board': 'test'}).json()['imported'] == 0
    assert test_client.get(API + '/live-jobs', headers=headers).json()[0]['is_active'] is False
    insights = test_client.get(API + '/market-insights', headers=headers).json()
    assert insights['current']['active_postings'] == 0
    stranger, _ = register('market-insights-stranger@example.com')
    assert test_client.get(API + '/market-insights', headers=stranger).json()['current'] is None
    assert test_client.post(API + '/live-jobs/import', headers=headers, json={'board': '../localhost'}).status_code == 422


def test_job_sources_preserve_first_seen_and_flag_likely_reposts_for_review(test_client, register, monkeypatch):
    headers, _ = register()
    description = 'Build reliable Python services, document APIs, review code, mentor teammates, improve database performance, and collaborate with product and design teams.'
    async def greenhouse(board):
        return {'jobs': [{'id': 1, 'title': 'Software Engineer', 'location': {'name': 'Remote'},
            'content': description, 'created_at': '2026-09-01T12:00:00Z',
            'absolute_url': 'https://boards.greenhouse.io/acme/jobs/1'}]}
    monkeypatch.setattr('app.runtime.reach.fetch_board', greenhouse)
    assert test_client.post(API + '/live-jobs/import', headers=headers, json={'board': 'acme'}).status_code == 200
    first = test_client.get(API + '/live-jobs', headers=headers).json()[0]
    first_seen = first['first_seen_at']
    assert first['posted_at'] == '2026-09-01'
    assert first['last_seen_at'] == first_seen

    async def lever(board):
        return [{'id': 'copy-1', 'text': 'Software Engineer', 'categories': {'team': 'acme', 'location': 'Remote'},
            'description': description, 'createdAt': 1788264000000,
            'hostedUrl': 'https://jobs.lever.co/acme/copy-1'}]
    monkeypatch.setattr('app.runtime.reach.fetch_lever_board', lever)
    assert test_client.post(API + '/live-jobs/import', headers=headers,
        json={'provider': 'lever', 'board': 'acme'}).status_code == 200
    jobs = test_client.get(API + '/live-jobs', headers=headers).json()
    original = next(job for job in jobs if job['url'].endswith('/jobs/1'))
    repost = next(job for job in jobs if job['url'].endswith('/copy-1'))
    assert original['first_seen_at'] == first_seen
    assert repost['possible_duplicate_of'] == original['id']
    assert repost['posted_at'] == '2026-09-01'


def test_market_trends_need_comparable_dated_snapshots_and_never_invent_a_forecast(test_client, register, monkeypatch):
    class FrozenDateTime(RealDateTime):
        current = RealDateTime(2026, 1, 1, 12, tzinfo=timezone.utc)

        @classmethod
        def now(cls, tz=None):
            return cls.current.astimezone(tz) if tz else cls.current.replace(tzinfo=None)

    monkeypatch.setattr('app.runtime.reach.datetime', FrozenDateTime)
    headers, _ = register()

    async def changing_board(board):
        count = 2 if FrozenDateTime.current < RealDateTime(2026, 1, 29, 0, tzinfo=timezone.utc) else 3
        return {'jobs': [
            {'id': index, 'title': f'Engineer {index}', 'location': {'name': 'Remote'},
             'content': '<p>Python and SQL required</p>',
             'absolute_url': f'https://boards.greenhouse.io/acme/jobs/{index}'}
            for index in range(1, count + 1)
        ]}

    monkeypatch.setattr('app.runtime.reach.fetch_board', changing_board)
    for offset in [0, 1, 2, 3, 4, 5, 6, 28, 29, 30, 31, 32, 33, 34]:
        FrozenDateTime.current = RealDateTime(2026, 1, 1, 12, tzinfo=timezone.utc) + timedelta(days=offset)
        response = test_client.post(API + '/live-jobs/import', headers=headers, json={'board': 'acme'})
        assert response.status_code == 200

    insights = test_client.get(API + '/market-insights', headers=headers).json()
    assert insights['trend_status'] == 'available'
    assert insights['trend']['change_percent'] == 50.0
    assert insights['skill_trends']
    assert insights['forecast'] is None
    assert 'out-of-sample backtest' in insights['forecast_note']


def test_social_drafts_use_licensed_parser_and_enforce_ownership(test_client, register):
    headers, _ = register()
    body = {'title': 'Project notes', 'content': 'I built a small project and learned from it.', 'kind': 'comment',
            'source_url': 'https://www.linkedin.com/posts/test-activity-7448808898326654978-abcd'}
    response = test_client.post(API + '/social/drafts', headers=headers, json=body)
    assert response.status_code == 201
    draft = response.json()
    assert draft['source_reference']['post_urn'] == 'urn:li:activity:7448808898326654978'
    assert draft['published'] is False
    assert test_client.post(API + '/social/drafts', headers=headers,
        json={**body, 'source_url': body['source_url'].replace('linkedin.com', 'linkedin.com.evil.test')}).status_code == 422
    stranger, _ = register('social-stranger@example.com')
    assert test_client.delete(API + '/social/drafts/' + draft['id'], headers=stranger).status_code == 404
    assert test_client.delete(API + '/social/drafts/' + draft['id'], headers=headers).status_code == 204


def test_linkedin_connect_flow_checks_publora_account_and_hides_key(test_client, register, monkeypatch):
    headers, _ = register()
    assert test_client.get(API + '/social/channels', headers=headers).status_code == 409
    key = 'sk_test_limitless_secret_key_12345'
    assert test_client.post(API + '/social/connections/provider', headers=headers,
        json={'name': 'publora', 'value': key}).status_code == 200

    class Response:
        status_code = 200
        def json(self):
            return {'connections': [
                {'platformId': 'linkedin-demo-123', 'name': 'My LinkedIn'},
                {'platformId': 'instagram-demo', 'name': 'Instagram'},
            ]}

    class Client:
        def __init__(self, **kwargs): pass
        async def __aenter__(self): return self
        async def __aexit__(self, *args): pass
        async def get(self, url, headers):
            assert url.endswith('/platform-connections')
            assert headers['x-publora-key'] == key
            return Response()

    monkeypatch.setattr('app.runtime.social_engine.httpx.AsyncClient', Client)
    channels = test_client.get(API + '/social/channels', headers=headers)
    assert channels.status_code == 200
    assert channels.json() == [{'id': 'linkedin-demo-123', 'name': 'My LinkedIn'}]
    assert key not in channels.text
    assert key not in test_client.get(API + '/social/engine', headers=headers).text


def test_lever_public_board_import_maps_internships_and_validates_employer_urls(test_client, register, monkeypatch):
    async def fake_lever(site):
        assert site == 'acme'
        return [
            {'id': 'role-1', 'text': 'Product Design Intern', 'categories': {'location': 'Remote', 'team': 'Design', 'commitment': 'Intern'},
             'description': '<p>Work with Figma and user research.</p>', 'hostedUrl': 'https://jobs.lever.co/acme/role-1'},
            {'id': 'role-2', 'text': 'Unsafe posting', 'categories': {}, 'description': 'Python',
             'hostedUrl': 'https://jobs.lever.co.evil.test/acme/role-2'},
        ]
    monkeypatch.setattr('app.runtime.reach.fetch_lever_board', fake_lever)
    headers, _ = register()
    response = test_client.post(API + '/live-jobs/import', headers=headers, json={'provider': 'lever', 'board': 'acme'})
    assert response.status_code == 200 and response.json()['imported'] == 1
    job = test_client.get(API + '/live-jobs', headers=headers).json()[0]
    assert job['type'] == 'internship'
    assert job['location'] == 'Remote'
    assert job['source'] == 'Lever public job board'
    assert job['url'] == 'https://jobs.lever.co/acme/role-1'


def test_ai_resume_connection_and_generation_are_user_scoped_and_keep_key_private(test_client, register, monkeypatch):
    headers, _ = register()
    mission = test_client.post(API + '/missions', headers=headers, json={'skill_id': 'python'}).json()
    assert test_client.post(API + f"/missions/{mission['id']}/complete", headers=headers, json={
        'artifact_url': 'https://github.com/example/python-api',
        'description': 'Built a Python API project with documented routes, request validation and tests.',
        'hours_spent': 8,
    }).status_code == 200
    job = {'title': 'Backend Intern', 'location': {'name': 'Remote'}, 'content': '<p>Python, SQL and APIs.</p>',
           'absolute_url': 'https://boards.greenhouse.io/test/jobs/22', 'id': 22}
    async def fake_board(board): return {'jobs': [job]}
    monkeypatch.setattr('app.runtime.reach.fetch_board', fake_board)
    test_client.post(API + '/live-jobs/import', headers=headers, json={'board': 'test'})
    listing = test_client.get(API + '/live-jobs', headers=headers).json()[0]
    packet = test_client.post(API + '/apply-queue/prepare', headers=headers, json={'job_ids': [listing['id']]}).json()[0]
    assert test_client.get(API + '/dashboard', headers=headers).json()['application_queue'] == {'total': 1, 'ready_for_review': 1}
    assert test_client.get(API + '/resume-ai/connection', headers=headers).json()['configured'] is False
    key = 'sk-test-resume-key-1234567890'
    connected = test_client.post(API + '/resume-ai/connection', headers=headers, json={'api_key': key, 'model': 'gpt-4.1-mini'})
    assert connected.status_code == 200 and key not in connected.text

    class Response:
        status_code = 200
        def raise_for_status(self): pass
        def json(self): return {'choices': [{'message': {'content': 'Jordan Example\nBackend Intern\n\nProjects\nPython API project\n\nEducation\nSource résumé details.'}}]}
    class Client:
        def __init__(self, **kwargs): pass
        async def __aenter__(self): return self
        async def __aexit__(self, *args): pass
        async def post(self, url, headers, json):
            assert url.endswith('/chat/completions')
            assert headers['Authorization'] == f'Bearer {key}'
            assert json['messages'][1]['content'].find('Backend Intern') >= 0
            return Response()
    monkeypatch.setattr('app.runtime.reach.httpx.AsyncClient', Client)
    generated = test_client.post(API + f"/apply-queue/{packet['id']}/tailor-resume", headers=headers, json={'consent': True})
    assert generated.status_code == 200
    assert 'Python API project' in generated.json()['generated_resume_text']
    assert key not in generated.text
    current = generated.json()
    assert current['resume']['guard'] == 'PASS'
    approved = test_client.post(API + f"/apply-queue/{packet['id']}/approve", headers=headers,
        json={'approved': True, 'version': current['version']})
    assert approved.status_code == 200 and approved.json()['status'] == 'approved_for_handoff'
    submitted = test_client.patch(API + f"/apply-queue/{packet['id']}/progress", headers=headers, json={'status': 'submitted'})
    assert submitted.status_code == 200 and submitted.json()['user_reported_status'] is True
    assert test_client.patch(API + f"/apply-queue/{packet['id']}/progress", headers=headers, json={'status': 'interview'}).json()['status'] == 'interview'
    stranger, _ = register('resume-stranger@example.com')
    assert test_client.get(API + '/resume-ai/connection', headers=stranger).json()['configured'] is False
    assert test_client.post(API + f"/apply-queue/{packet['id']}/tailor-resume", headers=stranger, json={'consent': True}).status_code == 404


def test_gemini_authorization_key_can_power_social_and_resume_drafts_without_exposure(test_client, register):
    headers, _ = register()
    key = 'AQ.' + 'x' * 40
    saved = test_client.post(API + '/resume-ai/connection', headers=headers, json={
        'api_key': key, 'model': 'gemini-flash-latest', 'provider': 'gemini'
    })
    assert saved.status_code == 200
    assert key not in saved.text
    assert saved.json() == {'saved': True, 'provider': 'gemini', 'model': 'gemini-flash-latest'}
    status = test_client.get(API + '/resume-ai/connection', headers=headers)
    assert status.json() == {'configured': True, 'provider': 'gemini', 'model': 'gemini-flash-latest'}
    assert key not in status.text


def test_dashboard_automation_preference_and_career_calendar_are_user_scoped(test_client, register):
    headers, _ = register()
    assert test_client.get(API + '/dashboard', headers=headers).json()['application_queue'] == {'total': 0}
    assert test_client.get(API + '/automation/preferences', headers=headers).json() == {
        'auto_prepare_matched': False, 'mode': 'prepare_only'
    }
    enabled = test_client.put(API + '/automation/preferences', headers=headers,
        json={'auto_prepare_matched': True})
    assert enabled.json() == {'auto_prepare_matched': True, 'mode': 'prepare_only'}
    assert test_client.post(API + '/automation/prepare-matches', headers=headers).json()['enabled'] is True
    assert test_client.post(API + '/career-calendar', headers=headers, json={
        'title': 'Interview with Acme', 'starts_at': '2026-10-08T10:00:00+05:30', 'kind': 'interview'
    }).status_code == 201
    event = test_client.get(API + '/career-calendar', headers=headers).json()[0]
    assert event['title'] == 'Interview with Acme' and event['kind'] == 'interview'
    assert test_client.post(API + '/career-calendar', headers=headers, json={
        'title': 'Missing timezone', 'starts_at': '2026-10-08T10:00:00', 'kind': 'reminder'
    }).status_code == 422
    stranger, _ = register('calendar-stranger@example.com')
    assert test_client.get(API + '/career-calendar', headers=stranger).json() == []
    assert test_client.delete(API + '/career-calendar/' + event['id'], headers=stranger).status_code == 404
    assert test_client.delete(API + '/career-calendar/' + event['id'], headers=headers).status_code == 204
