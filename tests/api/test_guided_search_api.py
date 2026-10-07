API = "/api/v1"


def test_guided_search_is_user_scoped_excludes_demo_and_returns_explanations(test_client, register, monkeypatch):
    headers, _ = register()
    stranger, _ = register("guided-stranger@example.com")

    async def board(_):
        return {"jobs": [
            {"id": 1, "title": "Data Analyst", "location": {"name": "Bengaluru"},
             "content": "Use Python and SQL to analyze data and create dashboards.",
             "absolute_url": "https://boards.greenhouse.io/test/jobs/1"},
            {"id": 2, "title": "Frontend Engineer", "location": {"name": "Remote"},
             "content": "Build React interfaces with TypeScript.",
             "absolute_url": "https://boards.greenhouse.io/test/jobs/2"},
        ]}

    monkeypatch.setattr("app.runtime.reach.fetch_board", board)
    assert test_client.post(API + "/live-jobs/import", headers=headers, json={"board": "test"}).status_code == 200
    response = test_client.post(API + "/live-jobs/guided-search", headers=headers, json={
        "query": "data analyst", "location": "Bengaluru", "target_skills": ["python"]
    })
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["result_count"] == 2
    assert result["model"]["corpus_size"] == 2
    assert result["model"]["supervised"] is False
    assert result["results"][0]["title"] == "Data Analyst"
    assert result["results"][0]["match_reasons"]["location_match"] is True
    assert test_client.post(API + "/live-jobs/guided-search", headers=stranger,
        json={"query": "data analyst"}).json()["result_count"] == 0

