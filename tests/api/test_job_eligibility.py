API = "/api/v1"


def test_eligibility_details_require_consent_and_category_export_opt_in(test_client, register):
    headers, _ = register()
    rejected = test_client.patch(API + "/users/me", headers=headers, json={"category": "obc"})
    assert rejected.status_code == 422
    saved = test_client.patch(
        API + "/users/me",
        headers=headers,
        json={"eligibility_consent": True, "qualification": "graduate", "date_of_birth": "2000-01-02", "category": "obc"},
    )
    assert saved.status_code == 200
    assert test_client.get(API + "/privacy/export", headers=headers).json()["profile"].get("category") is None
    assert test_client.patch(API + "/users/me", headers=headers, json={"category_export_consent": True}).status_code == 200
    assert test_client.get(API + "/privacy/export", headers=headers).json()["profile"]["category"] == "obc"
    revoked = test_client.patch(API + "/users/me", headers=headers, json={"eligibility_consent": False})
    assert revoked.status_code == 200
    assert revoked.json()["date_of_birth"] is None
    assert revoked.json()["category"] is None


def test_eligible_jobs_requires_profile_consent_and_returns_private_listings(test_client, register, monkeypatch):
    async def fake_board(board):
        return {"jobs": [{"id": 1, "title": "Engineer", "location": {"name": "Pune, Maharashtra"},
            "content": "Build software", "absolute_url": "https://boards.greenhouse.io/test/jobs/1"}]}

    monkeypatch.setattr("app.runtime.reach.fetch_board", fake_board)
    headers, _ = register()
    assert test_client.get(API + "/jobs/eligible?eligible_for_me=true", headers=headers).status_code == 409
    test_client.post(API + "/live-jobs/import", headers=headers, json={"board": "test"})
    test_client.patch(API + "/users/me", headers=headers, json={"eligibility_consent": True, "qualification": "graduate"})
    jobs = test_client.get(API + "/jobs/eligible?eligible_for_me=true&state=Maharashtra", headers=headers)
    assert jobs.status_code == 200
    assert jobs.json() == []
    all_jobs = test_client.get(API + "/jobs/eligible?state=Maharashtra", headers=headers)
    assert len(all_jobs.json()) == 1
    assert all_jobs.json()[0]["eligibility_result"]["status"] == "needs_review"
    assert all_jobs.json()[0]["source_type"] == "private"
