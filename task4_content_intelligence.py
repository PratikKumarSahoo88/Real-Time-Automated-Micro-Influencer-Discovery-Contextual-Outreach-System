"""
task4_content_intelligence.py — Content Context Analysis Layer
task5_brand_fit.py — Brand–Creator Fit Matching Engine

Task 4: Analyzes content signals (titles, descriptions, hashtags, keywords)
        to classify creator content intent — NOT bio assumptions.

Task 5: Scores each creator against brand context using a weighted fit formula.
"""

import math
from config import (
    FIT_WEIGHT_KEYWORD_MATCH,
    FIT_WEIGHT_SEGMENT_ALIGN,
    FIT_WEIGHT_ENGAGEMENT_RATE,
    FIT_WEIGHT_RECENCY,
    FIT_SCORE_THRESHOLD,
    COLLAB_STRATEGIES,
    BRAND_CONTEXT,
    SEGMENTS,
)


# ─────────────────────────────────────────────────────────────────────────────
#  TASK 4 — CONTENT CONTEXT INTELLIGENCE
# ─────────────────────────────────────────────────────────────────────────────

# Content intent taxonomy — mapped to detectable signal phrases
CONTENT_INTENT_MAP = {
    "education": {
        "olympiad_readiness": [
            "olympiad", "imo", "ntse", "nso", "igko", "sof", "silverzone",
            "science olympiad", "math olympiad", "qualify", "rank", "medal"
        ],
        "exam_preparation": [
            "cbse", "board exam", "preparation", "revision", "sample paper",
            "previous year", "model paper", "ncert", "class 10", "class 12"
        ],
        "reasoning_skills": [
            "reasoning", "logical", "aptitude", "mental math", "puzzle",
            "brain teaser", "IQ", "pattern", "series", "coding decoding"
        ],
        "student_competition": [
            "competition", "scholarship", "talent test", "quiz competition",
            "school competition", "interschool", "national level"
        ],
        "concept_teaching": [
            "concept", "explained", "tricks", "shortcut", "method",
            "how to solve", "formula", "theorem", "derivation"
        ],
    },
    "beauty": {
        "skincare_routine": ["routine", "am pm", "moisturiser", "serum", "toner", "cleanser"],
        "dermatologist_advice": ["dermatologist", "doctor", "skin type", "acne", "pigmentation"],
        "makeup_tutorial": ["tutorial", "look", "glam", "cut crease", "no makeup makeup"],
        "product_review": ["review", "honest", "worth it", "rating", "recommendation"],
        "affordable_finds": ["affordable", "budget", "drugstore", "under 500", "cheap"],
    },
    "fintech": {
        "investing_basics": ["sip", "mutual fund", "lump sum", "portfolio", "returns", "compounding"],
        "budgeting_advice": ["budget", "50-30-20", "expenses", "savings rate", "monthly budget"],
        "credit_literacy": ["credit score", "cibil", "credit card", "limit", "emi", "repayment"],
        "tax_planning": ["tax", "80c", "itr", "form 16", "tds", "tax saving"],
        "stock_analysis": ["stock", "nifty", "sensex", "smallcap", "midcap", "pe ratio"],
    },
}


def analyze_content_signals(profile: dict, industry: str) -> dict:
    """
    Analyze a creator's content signals and return detected intents + scores.
    Classification is based purely on content text, NOT bio assumptions.

    Returns:
        {
          "detected_intents": ["olympiad_readiness", "concept_teaching"],
          "intent_scores": {"olympiad_readiness": 3, "concept_teaching": 2, ...},
          "primary_intent": "olympiad_readiness",
          "content_signal_strength": 0.78,
        }
    """
    # Build a comprehensive text corpus from all available content signals
    text_corpus = " ".join([
        profile.get("video_title", ""),
        profile.get("video_description", ""),
        profile.get("recent_video_title", ""),
        profile.get("recent_video_description", ""),
        profile.get("description", ""),
        profile.get("channel_keywords", ""),
        profile.get("discovery_keyword", ""),
        " ".join(profile.get("content_themes", [])),
    ]).lower()

    intent_map = CONTENT_INTENT_MAP.get(industry, CONTENT_INTENT_MAP["education"])
    intent_scores = {}

    for intent, signals in intent_map.items():
        score = sum(1 for sig in signals if sig.lower() in text_corpus)
        if score > 0:
            intent_scores[intent] = score

    detected_intents = sorted(intent_scores, key=intent_scores.get, reverse=True)
    primary_intent = detected_intents[0] if detected_intents else "general_content"

    # Signal strength = ratio of triggered intents to total possible
    total_possible = sum(len(v) for v in intent_map.values())
    total_triggered = sum(intent_scores.values())
    strength = min(total_triggered / max(total_possible * 0.3, 1), 1.0)   # normalized

    return {
        "detected_intents": detected_intents[:3],
        "intent_scores": intent_scores,
        "primary_intent": primary_intent,
        "content_signal_strength": round(strength, 3),
    }


# ─────────────────────────────────────────────────────────────────────────────
#  TASK 5 — BRAND–CREATOR FIT MATCHING ENGINE
# ─────────────────────────────────────────────────────────────────────────────

def score_keyword_match(profile: dict, brand_keywords: list[str]) -> float:
    """Score 0–1: how many brand keywords appear in the creator's content."""
    text = " ".join([
        profile.get("recent_video_title", ""),
        profile.get("video_title", ""),
        profile.get("description", ""),
        " ".join(profile.get("content_themes", [])),
    ]).lower()

    if not brand_keywords:
        return 0.5

    matches = sum(1 for kw in brand_keywords if kw.lower() in text)
    return min(matches / len(brand_keywords), 1.0)


def score_segment_alignment(profile: dict, industry: str) -> float:
    """Score 0–1: how well the creator's segment aligns with brand priority."""
    # Segment A is highest priority, B medium, C lower
    segment_scores = {"A": 1.0, "B": 0.7, "C": 0.5}
    return segment_scores.get(profile.get("segment", "C"), 0.5)


def score_engagement(engagement_rate: float) -> float:
    """
    Score 0–1 based on engagement rate.
    Benchmarks for YouTube micro-influencers:
      < 1%   = low (0.2)
      1–3%   = average (0.5)
      3–6%   = good (0.75)
      > 6%   = excellent (1.0)
    """
    if engagement_rate < 1:
        return 0.2
    elif engagement_rate < 3:
        return 0.5 + (engagement_rate - 1) / 2 * 0.25   # 0.5 → 0.75
    elif engagement_rate < 6:
        return 0.75 + (engagement_rate - 3) / 3 * 0.25  # 0.75 → 1.0
    else:
        return 1.0


def score_recency(days_since_post: int | None) -> float:
    """
    Score 0–1 based on how recently the creator posted.
    0–7 days = 1.0, 8–30 = 0.8, 31–60 = 0.6, >60 = 0.3
    """
    if days_since_post is None:
        return 0.5
    if days_since_post <= 7:
        return 1.0
    elif days_since_post <= 30:
        return 0.8
    elif days_since_post <= 60:
        return 0.6
    else:
        return 0.3


def compute_brand_fit_score(profile: dict, industry: str) -> dict:
    """
    Compute the final brand–creator fit score using weighted formula.

    Score = (keyword_match × 0.40) + (segment_align × 0.30)
            + (engagement × 0.20) + (recency × 0.10)

    Returns:
        {
          "fit_score": 0.82,
          "fit_grade": "A",
          "component_scores": {...},
          "recommended_collab": ["Paid Sponsorship", "Ambassador Program"],
        }
    """
    # Get brand keywords for this industry (from segment definitions)
    brand_kws = []
    for seg_data in SEGMENTS.get(industry, {}).values():
        brand_kws.extend(seg_data.get("keywords", []))

    kw_score  = score_keyword_match(profile, brand_kws)
    seg_score = score_segment_alignment(profile, industry)
    eng_score = score_engagement(profile.get("engagement_rate_pct", 0))
    rec_score = score_recency(profile.get("days_since_last_post"))

    fit_score = (
        kw_score  * FIT_WEIGHT_KEYWORD_MATCH
        + seg_score * FIT_WEIGHT_SEGMENT_ALIGN
        + eng_score * FIT_WEIGHT_ENGAGEMENT_RATE
        + rec_score * FIT_WEIGHT_RECENCY
    )
    fit_score = round(fit_score, 3)

    # Grade
    if fit_score >= 0.80:
        grade = "A"
    elif fit_score >= 0.65:
        grade = "B"
    elif fit_score >= 0.50:
        grade = "C"
    else:
        grade = "D"

    # Collaboration strategy recommendation from config
    segment = profile.get("segment", "C")
    collab = COLLAB_STRATEGIES.get(industry, {}).get(segment, ["Barter Collaboration"])

    return {
        "fit_score": fit_score,
        "fit_grade": grade,
        "is_qualified": fit_score >= FIT_SCORE_THRESHOLD,
        "component_scores": {
            "keyword_match":   round(kw_score, 3),
            "segment_align":   round(seg_score, 3),
            "engagement_rate": round(eng_score, 3),
            "recency":         round(rec_score, 3),
        },
        "recommended_collab": collab,
    }


def analyze_and_score(profiles: list[dict], industry: str) -> list[dict]:
    """
    Apply Task 4 content intelligence + Task 5 brand-fit scoring to all profiles.
    Returns enriched profiles sorted by fit_score descending.
    Only profiles above threshold are returned.
    """
    print("═" * 60)
    print("  TASK 4 — CONTENT CONTEXT INTELLIGENCE LAYER")
    print("  TASK 5 — BRAND–FIT MATCHING ENGINE")
    print("═" * 60)

    qualified = []

    for p in profiles:
        # Task 4: content signal analysis
        signals = analyze_content_signals(p, industry)
        p["content_intelligence"] = signals

        # Task 5: brand-fit scoring
        fit = compute_brand_fit_score(p, industry)
        p.update(fit)

        if fit["is_qualified"]:
            qualified.append(p)

    # Sort by fit_score descending
    qualified.sort(key=lambda x: x["fit_score"], reverse=True)

    # Grade distribution
    grades = {"A": 0, "B": 0, "C": 0, "D": 0}
    for p in qualified:
        grades[p.get("fit_grade", "D")] += 1

    print(f"  Scored {len(profiles)} creators → {len(qualified)} qualified (score ≥ {FIT_SCORE_THRESHOLD})")
    print(f"  Grade distribution: A={grades['A']} | B={grades['B']} | C={grades['C']}")
    print()
    return qualified