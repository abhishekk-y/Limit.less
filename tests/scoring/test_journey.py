from app.runtime.catalog import TAXONOMY

from packages.scoring.journey import eligibility, extract_skills, match, plan, skill_score


def test_claims_are_not_evidence():
    assert skill_score([{"kind": "resume_claim"}])["score"] == 0
    assert skill_score([{"kind": "project", "artifact_url": "https://example.com"}])["score"] == 30


def test_hand_calculated_matching():
    assert match({"python": 30, "sql": 60}, ["python", "sql", "git"])["score"] == 30
    assert match({}, [])["score"] == 0


def test_no_universal_age_relaxation_or_unknown_pass():
    assert eligibility({"age": 32, "category": "SC"}, {"max_age": 30})["status"] == "MISSING"
    assert (
        eligibility({"age": 32, "category": "SC"}, {"max_age": 30, "age_relaxations": {"SC": 5}})["status"]
        == "PASS"
    )
    assert eligibility({}, {"max_age": 30})["status"] == "CONDITIONAL"
    assert eligibility({}, {"unknown_rule": 1})["status"] == "CONDITIONAL"


def test_prerequisite_budget_and_order():
    result = plan({}, ["kubernetes"], TAXONOMY, 40)
    assert [s["id"] for s in result["steps"]] == ["linux", "docker", "kubernetes"]
    assert result["hours"] == 40
    assert result["projected_score"] == 50
    assert plan({}, ["kubernetes"], TAXONOMY, 39)["steps"] == []


def test_extraction_word_boundaries():
    assert extract_skills("I used Python and SQL; unrelated: reactivate.", TAXONOMY) == ["python", "sql"]
