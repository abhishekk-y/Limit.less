"""Per-user TF-IDF retrieval and transparent skill evidence ranking.

This is an unsupervised relevance ranker fit on the current user's active,
non-demo job descriptions. It does not estimate hiring probability and does
not consume SAS challenge files or another user's listings.
"""

from __future__ import annotations

import math
import re
from collections import Counter

TOKEN_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9+#.]{1,30}")
MODEL_VERSION = "guided-tfidf-1.0"


def _tokens(text: str) -> list[str]:
    return [token.casefold() for token in TOKEN_RE.findall(text or "")]


def _document(job: dict) -> list[str]:
    # Title and detected skills are emphasized; description remains searchable.
    title = _tokens(str(job.get("title", ""))) * 3
    skills = _tokens(" ".join(job.get("skills", []))) * 4
    description = _tokens(str(job.get("description", ""))[:12000])
    return title + skills + description


def _cosine(left: Counter, right: Counter) -> float:
    if not left or not right:
        return 0.0
    dot = sum(value * right.get(token, 0.0) for token, value in left.items())
    norm_left = math.sqrt(sum(value * value for value in left.values()))
    norm_right = math.sqrt(sum(value * value for value in right.values()))
    return dot / (norm_left * norm_right) if norm_left and norm_right else 0.0


def rank_jobs(
    jobs: list[dict],
    *,
    query: str,
    location: str = "",
    target_skills: list[str] | None = None,
    profile_skill_scores: dict[str, float] | None = None,
) -> dict:
    """Fit corpus IDF weights and return ranked jobs with reason codes."""
    target_skills = list(dict.fromkeys(s.casefold().strip() for s in (target_skills or []) if s.strip()))
    profile_skill_scores = {str(k).casefold(): max(0.0, min(100.0, float(v))) for k, v in (profile_skill_scores or {}).items()}
    docs = [_document(job) for job in jobs]
    doc_freq = Counter(token for doc in docs for token in set(doc))
    n_docs = len(docs)
    idf = {token: math.log(1 + (n_docs + 1) / (count + 1)) for token, count in doc_freq.items()}

    query_tokens = _tokens(query) + _tokens(" ".join(target_skills)) * 2
    query_tf = Counter(query_tokens)
    query_vec = Counter({token: count * idf.get(token, math.log(n_docs + 1)) for token, count in query_tf.items()})

    ranked = []
    for job, tokens in zip(jobs, docs):
        tf = Counter(tokens)
        vector = Counter({token: (1 + math.log(count)) * idf.get(token, 0.0) for token, count in tf.items()})
        text_relevance = _cosine(query_vec, vector)
        # Normalize against the best candidate in this result set below.
        job_skills = list(dict.fromkeys(str(s).casefold() for s in job.get("skills", [])))
        searchable_text = f"{job.get('title', '')} {job.get('description', '')}".casefold()
        matched_targets = [s for s in target_skills if s in job_skills or s in searchable_text]
        matched = [s for s in job_skills if s in profile_skill_scores and profile_skill_scores[s] >= 50]
        missing = [s for s in job_skills if s not in matched]
        profile_coverage = (
            sum(profile_skill_scores[s] / 100 for s in matched) / len(job_skills)
            if job_skills and profile_skill_scores
            else None
        )
        target_coverage = len(matched_targets) / len(target_skills) if target_skills else None
        location_match = bool(location.strip()) and location.casefold() in str(job.get("location", "")).casefold()
        ranked.append({
            **job,
            "_text_relevance": text_relevance,
            "_profile_coverage": profile_coverage,
            "_target_coverage": target_coverage,
            "_location_match": location_match,
            "matched_profile_skills": matched,
            "missing_profile_skills": missing,
            "matched_target_skills": matched_targets,
            "missing_target_skills": [s for s in target_skills if s not in matched_targets],
        })

    max_relevance = max((row["_text_relevance"] for row in ranked), default=0.0)
    for row in ranked:
        relevance = row.pop("_text_relevance")
        coverage = row.pop("_profile_coverage")
        target_coverage = row.pop("_target_coverage")
        location_match = row.pop("_location_match")
        lexical = relevance / max_relevance if max_relevance else 0.0
        # Reweight only among available evidence dimensions; never silently
        # treat missing profile skills as a zero-quality user.
        parts = [("text_relevance", lexical, 0.55)]
        if target_coverage is not None:
            parts.append(("target_skill_coverage", target_coverage, 0.20))
        if coverage is not None:
            parts.append(("profile_skill_coverage", coverage, 0.20))
        if location.strip():
            parts.append(("location", 1.0 if location_match else 0.0, 0.05))
        weight_sum = sum(weight for _, _, weight in parts)
        score = 100 * sum(value * weight for _, value, weight in parts) / weight_sum if weight_sum else 0.0
        row["match_score"] = round(score, 1)
        row["match_breakdown"] = {name: round(100 * value, 1) for name, value, _ in parts}
        row["match_reasons"] = {
            "query_terms": query_tokens[:20],
            "matched_profile_skills": row["matched_profile_skills"],
            "missing_profile_skills": row["missing_profile_skills"],
            "matched_target_skills": row["matched_target_skills"],
            "missing_target_skills": row["missing_target_skills"],
            "location_match": location_match if location.strip() else None,
        }
        row["match_score_type"] = "relative relevance and evidence coverage; not hiring probability"
    ranked.sort(key=lambda item: (-item["match_score"], str(item.get("title", "")).casefold(), str(item.get("id", ""))))
    return {
        "results": ranked,
        "model": {
            "name": "Corpus-fitted TF-IDF retrieval + explicit profile evidence coverage",
            "version": MODEL_VERSION,
            "status": "corpus_fitted" if n_docs >= 2 else "small_corpus_fallback",
            "corpus_size": n_docs,
            "supervised": False,
            "fit_scope": "current user's active, non-demo listings in this request",
            "limitations": [
                "No relevance labels or user outcome data were used; this is not a supervised model.",
                "Scores are relative to the current user's imported listing set and are not comparable across searches.",
                "Skill tags use the current curated phrase taxonomy and may miss synonyms or novel terms.",
                "A match score is not the probability of interview, offer, or employment.",
            ],
        },
    }
