"""Deterministic, explainable scoring used by the executable career journey.

Scores describe evidence coverage, never probability of employment. No fabricated
confidence intervals: uncalibrated evidence weights always carry Low confidence.
"""

import re
from itertools import combinations


def lineage(formula, records, source="User evidence and DEMO taxonomy"):
    return {
        "source": source,
        "period": "Current saved profile",
        "record_count": records,
        "formula": formula,
        "model": "journey-v1",
        "confidence": "Low",
        "limitations": "Heuristic weights; not calibrated on hiring outcomes. Demo market is fictional.",
    }


def extract_skills(text, taxonomy):
    aliases = {
        "machine_learning": ["machine learning", "ml"],
        "power_bi": ["power bi"],
        "javascript": ["javascript", "js"],
        "typescript": ["typescript", "ts"],
    }
    return [
        key
        for key, item in taxonomy.items()
        if any(
            re.search(r"(?<!\w)" + re.escape(term) + r"(?!\w)", text, re.I)
            for term in aliases.get(key, [item["name"], key])
        )
    ]


def skill_score(evidence):
    # A resume claim alone is not proof. A submitted artifact is self-reported,
    # and only a separately verified artifact receives verification weight.
    artifacts = [e for e in evidence if e.get("kind") == "project" and e.get("artifact_url")]
    assessment = max((e.get("assessment", 0) for e in evidence if e.get("kind") == "assessment"), default=0)
    verified = any(e.get("verified", False) for e in artifacts)
    components = {
        "artifact": 30 if artifacts else 0,
        "assessment": round(assessment * 0.4, 2),
        "verification": 30 if verified else 0,
    }
    return {
        "score": round(sum(components.values()), 2),
        "components": components,
        "verified": verified,
        "lineage": lineage("30*has_artifact + 0.4*assessment_percent + 30*verified", len(evidence)),
    }


def match(skills, required):
    required = list(dict.fromkeys(required))
    contributions = {s: max(0, min(100, skills.get(s, 0))) for s in required}
    score = round(sum(contributions.values()) / len(required), 2) if required else 0
    return {
        "score": score,
        "breakdown": contributions,
        "missing_skills": [s for s in required if contributions[s] < 50],
        "lineage": lineage("mean(STS of required skills), missing=0", len(required)),
    }


def eligibility(profile, rules):
    reasons = []
    missing = []
    for field, rule, check in (
        ("age", "min_age", lambda a, b: a >= b),
        ("age", "max_age", lambda a, b: a <= b),
        ("education_level", "education_level", lambda a, b: a >= b),
        ("cgpa", "min_cgpa", lambda a, b: a >= b),
    ):
        if rule not in rules:
            continue
        if profile.get(field) is None:
            missing.append(field)
            continue
        threshold = rules[rule]
        if rule == "max_age":
            # Relaxation belongs to this notification, never a universal rule.
            threshold += rules.get("age_relaxations", {}).get(profile.get("category"), 0)
        if not check(profile[field], threshold):
            reasons.append(f"{field} does not satisfy {rule}: {threshold}")
    if rules.get("documents"):
        missing.extend(d for d in rules["documents"] if d not in profile.get("documents", []))
    if "domicile" in rules:
        if not profile.get("domicile"):
            missing.append("domicile")
        elif profile["domicile"] not in rules["domicile"]:
            reasons.append("Domicile is outside the permitted locations")
    supported = {
        "min_age",
        "max_age",
        "education_level",
        "min_cgpa",
        "age_relaxations",
        "documents",
        "domicile",
    }
    missing.extend(f"Unsupported rule: {key}" for key in rules if key not in supported)
    return {
        "status": "MISSING" if reasons else "CONDITIONAL" if missing else "PASS",
        "reasons": reasons,
        "missing": sorted(set(missing)),
        "lineage": lineage("Explicit per-opportunity rules; unknown values never pass", len(rules)),
    }


def plan(skills, target, taxonomy, budget=40):
    required = set(target)

    def closure(skill):
        result = {skill}
        for prerequisite in taxonomy[skill]["prerequisites"]:
            if skills.get(prerequisite, 0) < 50:
                result |= closure(prerequisite)
        return result

    candidates = set()
    for skill in required:
        if skills.get(skill, 0) < 50:
            candidates |= closure(skill)
    candidates = sorted(candidates)
    best, best_gain, best_hours = set(), 0, 0
    baseline = match(skills, target)["score"]
    # Exact bounded subset optimization for the small curated taxonomy.
    for size in range(len(candidates) + 1):
        for subset in combinations(candidates, size):
            selected = set(subset)
            hours = sum(taxonomy[s]["hours"] for s in selected)
            if hours > budget or any(not closure(s).issubset(selected) for s in selected):
                continue
            projected = {**skills, **{s: max(skills.get(s, 0), 50) for s in selected}}
            gain = match(projected, target)["score"] - baseline
            if gain > best_gain or (gain == best_gain and hours < best_hours):
                best, best_gain, best_hours = selected, gain, hours
    ordered = []

    def visit(skill):
        for prerequisite in taxonomy[skill]["prerequisites"]:
            if prerequisite in best:
                visit(prerequisite)
        if skill not in ordered:
            ordered.append(skill)

    for skill in sorted(best):
        visit(skill)
    return {
        "steps": [taxonomy[s] for s in ordered],
        "hours": best_hours,
        "budget": budget,
        "current_score": baseline,
        "projected_score": round(baseline + best_gain, 2),
        "opportunity_gain_per_hour": round(best_gain / best_hours, 3) if best_hours else 0,
        "lineage": lineage(
            "Maximize required-skill coverage within hours and prerequisites; projected STS=50 is a scenario",
            len(target),
        ),
        "projection_note": "Completing a mission does not guarantee a score of 50 or a job.",
    }
