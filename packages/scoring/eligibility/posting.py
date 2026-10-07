"""Eligibility checks for a dated job posting."""

from datetime import date

QUALIFICATION_LEVELS = {
    "10th": 1,
    "12th": 2,
    "diploma": 3,
    "graduate": 4,
    "postgraduate": 5,
    "phd": 6,
}

# Common central direct-recruitment defaults. The notification remains authoritative.
CENTRAL_RELAXATION_YEARS = {"sc": 5, "st": 5, "obc": 3, "ews": 0, "general": 0}


def age_on(dob: date, cutoff: date) -> int:
    return cutoff.year - dob.year - ((cutoff.month, cutoff.day) < (dob.month, dob.day))


def _date(value):
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value[:10])
        except ValueError:
            return None
    return None


def check(posting: dict, profile: dict) -> dict:
    reasons = []
    verify_notes = []
    reason_codes = []
    unknown = False
    today = date.today()
    has_requirements = any(
        posting.get(key) is not None
        for key in ("min_qualification", "max_age", "last_date")
    )
    if not has_requirements:
        unknown = True
        verify_notes.append("The posting has no structured eligibility requirements; verify the original notice.")
        reason_codes.append("requirements_missing")

    last_date = _date(posting.get("last_date"))
    if last_date and last_date < today:
        reasons.append("The application window has closed.")
        reason_codes.append("closed_window")
        eligible = False
    else:
        eligible = True

    minimum = posting.get("min_qualification")
    if minimum:
        candidate_level = QUALIFICATION_LEVELS.get(str(profile.get("qualification", "")).lower())
        required_level = QUALIFICATION_LEVELS.get(str(minimum).lower())
        if candidate_level is None or required_level is None:
            unknown = True
            verify_notes.append("Qualification details need to be checked in the official notice.")
            reason_codes.append("qualification_unknown")
        elif candidate_level < required_level:
            eligible = False
            reasons.append(f"This role requires at least {minimum} qualification.")
            reason_codes.append("qualification_mismatch")

    maximum_age = posting.get("max_age")
    if maximum_age is not None:
        dob = _date(profile.get("date_of_birth"))
        cutoff = _date(posting.get("age_cutoff"))
        if not dob or not cutoff:
            unknown = True
            verify_notes.append("Date of birth or the notice's age cutoff is missing.")
            reason_codes.append("age_details_missing")
        else:
            category = str(profile.get("category") or "general").lower()
            notification_relaxation = posting.get("relaxation") or {}
            relaxation = notification_relaxation.get(category)
            if relaxation is None:
                central_scope = posting.get("relaxation_scope") == "central_direct_recruitment"
                relaxation = CENTRAL_RELAXATION_YEARS.get(category, 0) if central_scope else 0
                verify_notes.append(
                    "Age relaxation uses a common central-government default; verify it in the official notification."
                    if central_scope
                    else "No age relaxation was assumed; verify the category rules in the official notification."
                )
                reason_codes.append("verify_relaxation")
            if age_on(dob, cutoff) > int(maximum_age) + int(relaxation):
                eligible = False
                reasons.append("Your age exceeds the listed upper age limit after the selected relaxation.")
                reason_codes.append("age_over_limit")

    if not eligible:
        status = "ineligible"
    elif unknown:
        eligible = None
        status = "needs_review"
    else:
        status = "eligible"
    return {"eligible": eligible, "status": status, "reasons": reasons, "reason_codes": reason_codes, "verify_notes": verify_notes}
