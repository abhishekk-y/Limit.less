from packages.scoring.guided_search import MODEL_VERSION, rank_jobs


def test_ranker_fits_idf_on_candidate_corpus_and_explains_skill_gaps():
    jobs = [
        {"id": "a", "title": "Data analyst", "location": "Bengaluru", "skills": ["python", "sql"], "description": "Build reports and analyze data"},
        {"id": "b", "title": "Frontend engineer", "location": "Remote", "skills": ["react", "typescript"], "description": "Build web interfaces"},
    ]
    result = rank_jobs(
        jobs,
        query="data analyst",
        location="Bengaluru",
        target_skills=["python"],
        profile_skill_scores={"python": 80},
    )
    assert result["model"]["version"] == MODEL_VERSION
    assert result["model"]["status"] == "corpus_fitted"
    assert result["model"]["supervised"] is False
    assert result["results"][0]["id"] == "a"
    assert result["results"][0]["match_reasons"]["matched_profile_skills"] == ["python"]
    assert "sql" in result["results"][0]["match_reasons"]["missing_profile_skills"]
    assert "not hiring probability" in result["results"][0]["match_score_type"]


def test_ranker_reports_small_corpus_and_does_not_claim_a_fit():
    result = rank_jobs([{"id": "a", "title": "Analyst", "skills": [], "description": ""}], query="analyst")
    assert result["model"]["status"] == "small_corpus_fallback"
    assert result["model"]["corpus_size"] == 1


def test_ranker_does_not_penalize_a_user_without_saved_skill_evidence():
    jobs = [{"id": "a", "title": "Analyst", "skills": ["python"], "description": "Python analyst"}]
    result = rank_jobs(jobs, query="analyst", profile_skill_scores={})
    assert "profile_skill_coverage" not in result["results"][0]["match_breakdown"]
