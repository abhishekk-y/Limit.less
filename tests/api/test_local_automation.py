import time

from app.runtime import automation, browser_apply

API = "/api/v1"


def test_local_worker_is_disabled_and_scoped_by_default(test_client, register):
    headers, _ = register()
    status = test_client.get(API + "/automation/local-status", headers=headers).json()
    assert status["enabled"] is False and status["ready"] is False
    response = test_client.post(
        API + "/automation/runs", headers=headers, json={"discover": True, "approved": True, "consent": True}
    )
    assert response.status_code == 409
    assert test_client.get(API + "/automation/runs").status_code == 401


def test_submission_run_uses_real_worker_result_and_private_source(test_client, register, monkeypatch):
    headers, _ = register()
    test_client.put(
        API + "/resume-builder",
        headers=headers,
        json={"summary": "I built Python applications at Example Studio.", "skills": ["Python"]},
    )

    async def board(_):
        return {
            "jobs": [
                {
                    "id": 1,
                    "title": "Python engineer",
                    "content": "Python applications",
                    "absolute_url": "https://boards.greenhouse.io/example/jobs/1",
                    "location": {"name": "Remote"},
                }
            ]
        }

    monkeypatch.setattr("app.runtime.reach.fetch_board", board)
    test_client.post(API + "/live-jobs/import", headers=headers, json={"board": "example"})
    job = test_client.get(API + "/live-jobs", headers=headers).json()[0]

    async def ready(*args):
        return {"ready": True}

    monkeypatch.setattr(automation, "local_status", ready)

    async def config(*args):
        return {"provider": "gemini", "model": "test", "api_key": "private-test-key"}

    monkeypatch.setattr("app.runtime.reach.resume_ai_config", config)

    async def tailor(*args):
        return {}

    monkeypatch.setattr("app.runtime.reach.tailor_resume", tailor)

    async def apply(job, applicant, source, resume, values, channel, cancelled):
        assert "Example Studio" in source and "Example Studio" in resume
        assert values["api_key"] == "private-test-key"
        return {"status": "submitted", "note": "Employer confirmed", "confirmation": "application received"}

    monkeypatch.setattr(browser_apply, "apply_to_job", apply)
    response = test_client.post(
        API + "/automation/runs",
        headers=headers,
        json={"job_ids": [job["id"]], "approved": True, "consent": True},
    )
    assert response.status_code == 202, response.text
    for _ in range(50):
        runs = test_client.get(API + "/automation/runs", headers=headers).json()
        if runs[0]["status"] in automation.TERMINAL:
            break
        time.sleep(0.02)
    assert runs[0]["status"] == "completed", runs
    assert runs[0]["items"][0]["status"] == "submitted"
    assert "private-test-key" not in str(runs)
    packet = test_client.get(API + "/apply-queue", headers=headers).json()[0]
    assert packet["submitted"] is True and packet["user_reported_status"] is False
    stranger, _ = register("other-worker@example.com")
    assert test_client.get(API + "/automation/runs", headers=stranger).json() == []
    assert (
        test_client.post(API + f"/automation/runs/{runs[0]['id']}/cancel", headers=stranger).status_code
        == 404
    )


def test_legacy_auto_apply_cannot_fabricate_a_submission(test_client, register):
    headers, _ = register()
    response = test_client.post(
        API + "/live-jobs/import", headers=headers, json={"board": "example", "auto_apply": True}
    )
    assert response.status_code == 409
    assert test_client.get(API + "/applications", headers=headers).json() == []


def test_uploaded_resume_allows_manual_review_without_project_certification(
    test_client, register, monkeypatch
):
    headers, _ = register()
    test_client.put(
        API + "/resume-builder", headers=headers, json={"summary": "I built Python applications."}
    )

    async def board(_):
        return {
            "jobs": [
                {
                    "id": 1,
                    "title": "Python engineer",
                    "content": "Python",
                    "absolute_url": "https://boards.greenhouse.io/example/jobs/1",
                    "location": {"name": "Remote"},
                }
            ]
        }

    monkeypatch.setattr("app.runtime.reach.fetch_board", board)
    test_client.post(API + "/live-jobs/import", headers=headers, json={"board": "example"})
    job = test_client.get(API + "/live-jobs", headers=headers).json()[0]
    packet = test_client.post(
        API + "/apply-queue/prepare", headers=headers, json={"job_ids": [job["id"]]}
    ).json()[0]
    assert packet["resume"]["guard"] == "BLOCKED" and packet["resume"]["source_available"] is True
    approved = test_client.post(
        API + f"/apply-queue/{packet['id']}/approve", headers=headers, json={"approved": True, "version": 1}
    )
    assert approved.status_code == 200 and approved.json()["submitted"] is False
