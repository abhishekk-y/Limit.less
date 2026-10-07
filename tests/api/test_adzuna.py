from fastapi import HTTPException

API = "/api/v1"


def test_adzuna_search_imports_and_deduplicates_listings_under_daily_budget(test_client, test_app, register, monkeypatch):
    test_app.state.settings.adzuna_app_id = "test-app"
    test_app.state.settings.adzuna_app_key = "test-key"
    test_app.state.settings.adzuna_daily_call_limit = 2
    async def fake_fetch(query, location, page, settings, db):
        calls = await __import__("app.runtime.reach", fromlist=["reserve_adzuna_call"]).reserve_adzuna_call(db, settings.adzuna_daily_call_limit)
        if calls is None:
            raise HTTPException(429, "daily cap")
        return {"results": [{"id": "9001", "title": "Data Analyst Intern", "created": "2026-10-01T12:00:00Z",
            "description": "Python and SQL analysis", "redirect_url": "https://www.adzuna.in/details/9001",
            "location": {"display_name": "Pune, Maharashtra"}, "company": {"display_name": "Example"}}]}

    monkeypatch.setattr("app.runtime.reach.fetch_adzuna_page", fake_fetch)
    headers, _ = register()
    body = {"query": "data analyst", "location": "Pune"}
    first = test_client.post(API + "/live-jobs/adzuna-search", headers=headers, json=body)
    second = test_client.post(API + "/live-jobs/adzuna-search", headers=headers, json=body)
    assert first.status_code == second.status_code == 200
    jobs = test_client.get(API + "/live-jobs", headers=headers).json()
    assert len(jobs) == 1
    assert jobs[0]["source_provider"] == "adzuna"
    assert jobs[0]["source_type"] == "internship"
    assert jobs[0]["last_date"] is None
    insight = test_client.get(API + "/market-insights", headers=headers).json()
    assert insight["current"]["active_postings"] == 1
    assert insight["current"]["internship_postings"] == 1
    assert any(source.startswith("adzuna:in:") for source in insight["current"]["sources"])
    assert insight["current"]["source_checks"][0]["active_count"] == 1
    assert test_client.get(API + "/sources/status", headers=headers).json()["adzuna"]["calls_today"] == 2
    capped = test_client.post(API + "/live-jobs/adzuna-search", headers=headers, json=body)
    assert capped.status_code == 429


def test_adzuna_search_without_server_credentials_stays_disabled(test_client, register):
    headers, _ = register()
    response = test_client.post(API + "/live-jobs/adzuna-search", headers=headers, json={"query": "developer"})
    assert response.status_code == 503
    status = test_client.get(API + "/sources/status", headers=headers).json()
    assert status["adzuna"]["configured"] is False
    assert status["categories"] == {"govt": 0, "psu": 0, "private": 0, "internship": 0}


def test_adzuna_one_step_connection_verifies_and_encrypts_account_credentials(test_client, test_app, register, monkeypatch):
    from app.runtime.reach import reserve_adzuna_call

    observed = []

    async def fake_fetch(query, location, page, settings, db):
        observed.append((settings.adzuna_app_id, settings.adzuna_app_key))
        await reserve_adzuna_call(db, settings.adzuna_daily_call_limit)
        return {"results": []}

    monkeypatch.setattr("app.runtime.reach.fetch_adzuna_page", fake_fetch)
    headers, _ = register()
    response = test_client.post(API + "/adzuna/connection", headers=headers, json={"app_id": "demo123", "app_key": "private-test-key"})
    assert response.status_code == 200
    assert response.json() == {"configured": True, "verified": True, "credential_source": "account"}
    assert observed == [("demo123", "private-test-key")]
    status = test_client.get(API + "/sources/status", headers=headers).json()["adzuna"]
    assert status["configured"] is True
    assert status["credential_source"] == "account"
    assert status["calls_today"] == 1
    connection = test_client.get(API + "/adzuna/connection", headers=headers).json()
    assert "app_key" not in connection and "private-test-key" not in str(connection)
    exported = test_client.get(API + "/privacy/export", headers=headers).json()
    assert all(record["kind"] != "integration_secret" for record in exported["records"])


def test_adzuna_search_uses_verified_account_credentials(test_client, register, monkeypatch):
    from app.runtime.reach import reserve_adzuna_call

    observed = []

    async def fake_fetch(query, location, page, settings, db):
        observed.append((settings.adzuna_app_id, settings.adzuna_app_key))
        await reserve_adzuna_call(db, settings.adzuna_daily_call_limit)
        return {"results": []}

    monkeypatch.setattr("app.runtime.reach.fetch_adzuna_page", fake_fetch)
    headers, _ = register()
    connected = test_client.post(API + "/adzuna/connection", headers=headers, json={"app_id": "demo123", "app_key": "private-test-key"})
    assert connected.status_code == 200
    searched = test_client.post(API + "/live-jobs/adzuna-search", headers=headers, json={"query": "developer"})
    assert searched.status_code == 200
    assert observed == [("demo123", "private-test-key"), ("demo123", "private-test-key")]
