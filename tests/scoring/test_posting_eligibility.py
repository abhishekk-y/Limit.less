from datetime import date

import pytest

from packages.scoring.eligibility.posting import age_on, check


def result(posting=None, profile=None):
    return check(posting or {}, profile or {})


def test_age_on_cutoff_uses_birthday_boundary():
    assert age_on(date(2000, 6, 15), date(2026, 6, 15)) == 26
    assert age_on(date(2000, 6, 16), date(2026, 6, 15)) == 25


def test_age_exactly_at_limit_is_eligible():
    assert result({"max_age": 26, "age_cutoff": "2026-06-15"}, {"date_of_birth": "2000-06-15"})["eligible"] is True


def test_age_one_day_over_limit_is_ineligible():
    assert result({"max_age": 25, "age_cutoff": "2026-06-15"}, {"date_of_birth": "2000-06-15"})["eligible"] is False


def test_age_is_not_calculated_at_today():
    assert result({"max_age": 25, "age_cutoff": "2025-06-15"}, {"date_of_birth": "2000-06-15"})["eligible"] is True


def test_missing_age_cutoff_needs_review():
    assert result({"max_age": 25}, {"date_of_birth": "2000-06-15"})["status"] == "needs_review"


def test_missing_date_of_birth_needs_review():
    assert result({"max_age": 25, "age_cutoff": "2026-06-15"})["status"] == "needs_review"


def test_expired_posting_is_closed():
    checked = result({"last_date": "2000-01-01"})
    assert checked["eligible"] is False
    assert checked["status"] == "ineligible"


def test_deadline_today_is_not_closed():
    assert result({"last_date": date.today().isoformat()})["eligible"] is True


@pytest.mark.parametrize(
    ("candidate", "required", "expected"),
    [("graduate", "diploma", True), ("diploma", "graduate", False), ("phd", "postgraduate", True), ("12th", "10th", True)],
)
def test_qualification_order(candidate, required, expected):
    assert result({"min_qualification": required}, {"qualification": candidate})["eligible"] is expected


def test_missing_qualification_needs_review():
    assert result({"min_qualification": "graduate"})["status"] == "needs_review"


def test_unknown_qualification_needs_review():
    assert result({"min_qualification": "graduate"}, {"qualification": "certificate"})["status"] == "needs_review"


def test_notification_relaxation_overrides_fallback():
    checked = result(
        {"max_age": 25, "age_cutoff": "2026-06-15", "relaxation": {"obc": 1}},
        {"date_of_birth": "1999-06-15", "category": "obc"},
    )
    assert checked["eligible"] is False
    assert checked["verify_notes"] == []


@pytest.mark.parametrize(("category", "years"), [("sc", 5), ("st", 5), ("obc", 3), ("ews", 0), ("general", 0)])
def test_common_central_relaxation_is_disclosed(category, years):
    checked = result(
        {"max_age": 25, "age_cutoff": "2026-06-15", "relaxation_scope": "central_direct_recruitment"},
        {"date_of_birth": "2000-06-15", "category": category},
    )
    assert checked["eligible"] is (years >= 1)
    assert any("verify it in the official notification" in note for note in checked["verify_notes"])


def test_missing_category_uses_general_without_relaxation():
    checked = result({"max_age": 25, "age_cutoff": "2026-06-15"}, {"date_of_birth": "2000-06-15"})
    assert checked["eligible"] is False


def test_posting_without_requirements_needs_review():
    checked = result()
    assert checked["status"] == "needs_review"
    assert checked["eligible"] is None
    assert "requirements_missing" in checked["reason_codes"]
