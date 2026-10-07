API = "/api/v1"


def start(client, headers, mode="practice"):
    return client.post(
        API + "/assessments/python/sessions",
        headers=headers,
        json={"mode": mode, "consent": True, "camera": True, "microphone": True, "fullscreen": True},
    )


def answer(session):
    correct = {
        "Which Python collection prevents duplicate values?": "set",
        "What does a context manager help control?": "Resource cleanup",
        "Which exception commonly indicates a missing dictionary key?": "KeyError",
        "How should you compare a value with None?": "value is None",
    }
    return {q["id"]: q["choices"].index(correct[q["prompt"]]) for q in session["questions"]}


def test_randomized_attempt_scoring_replay_and_ownership(test_client, register):
    headers, _ = register()
    session = start(test_client, headers).json()
    assert all("answer" not in q for q in session["questions"])
    stranger, _ = register("other-session@example.com")
    url = API + "/assessment-sessions/" + session["id"] + "/submit"
    body = {"answers": answer(session), "events": []}
    assert test_client.post(url, headers=stranger, json=body).status_code == 404
    response = test_client.post(url, headers=headers, json=body)
    assert response.json()["score"] == 100
    assert response.json()["evidence_added"] is True
    assert response.json()["verified"] is False
    assert test_client.post(url, headers=headers, json=body).status_code == 409


def test_sas_foundations_session_issues_only_the_limitless_assessment_badge(test_client, register):
    headers, _ = register()
    session = test_client.post(
        API + "/assessments/sas_foundations/sessions",
        headers=headers,
        json={"mode": "practice", "consent": True},
    ).json()
    correct = {
        "Which SAS procedure displays a table's columns, types, and attributes?": "PROC CONTENTS",
        "What is SAS WORK commonly used for?": "Temporary session output",
        "What does a LIBNAME statement normally define?": "A library reference to a data location",
        "Which procedure is a basic choice for one-way category counts?": "PROC FREQ",
        "When should two datasets be joined for analysis?": "Only with a meaningful, verified common key and justified question",
        "Where must the SAS hackathon source files and derived results stay under the current data rule?": "The organizer-approved SAS VFL environment",
        "What does NOT RUN mean on this project's evidence screen?": "No verified execution receipt exists",
        "Does passing a Limit.less quiz award an official SAS Institute certification?": "No; it awards only the clearly scoped Limit.less assessment badge",
    }
    answers = {q["id"]: q["choices"].index(correct[q["prompt"]]) for q in session["questions"]}
    response = test_client.post(API + "/assessment-sessions/" + session["id"] + "/submit",
        headers=headers, json={"answers": answers})
    assert response.status_code == 200
    assert response.json()["evidence_added"] is True
    assert response.json()["platform_credential"]["not_sas_issued"] is True


def test_monitored_interruption_withholds_evidence(test_client, register):
    headers, _ = register()
    session = start(test_client, headers, "monitored").json()
    base = API + "/assessment-sessions/" + session["id"]
    assert (
        test_client.post(base + "/signals", headers=headers, json={"events": ["tab_hidden"]}).status_code
        == 200
    )
    result = test_client.post(base + "/submit", headers=headers, json={"answers": answer(session)}).json()
    assert result["status"] == "review_required"
    assert result["evidence_added"] is False
    assert test_client.get(API + "/talent-twin", headers=headers).json()["skills"] == []
    history = test_client.get(API + "/assessment-sessions", headers=headers).json()
    assert history[0]["result"]["events"][0]["type"] == "tab_hidden"


def test_session_preflight_consent_and_export_minimization(test_client, register):
    headers, _ = register()
    url = API + "/assessments/python/sessions"
    assert (
        test_client.post(url, headers=headers, json={"mode": "monitored", "consent": False}).status_code
        == 422
    )
    assert (
        test_client.post(url, headers=headers, json={"mode": "monitored", "consent": True}).status_code == 422
    )
    start(test_client, headers)
    export = test_client.get(API + "/privacy/export", headers=headers).json()
    attempt = next(r for r in export["records"] if r["kind"] == "assessment_session")
    assert "key" not in attempt


def test_session_deadline_is_enforced_on_server(test_client, register, monkeypatch):
    headers, _ = register()
    session = start(test_client, headers).json()
    monkeypatch.setattr("app.runtime.assessment_sessions.time.time", lambda: session["expires_at"] + 1)
    result = test_client.post(
        API + "/assessment-sessions/" + session["id"] + "/submit",
        headers=headers,
        json={"answers": answer(session)},
    ).json()
    assert result["status"] == "expired"
    assert result["evidence_added"] is False
