"""
task2_filter_classify.py — Automated Filtering & Creator Segmentation
task3_enrich.py logic is also merged here for efficiency.

Filters by:
  - Follower range (5K–100K subscribers)
  - Region (India)
  - Content relevance (keyword match)
  - Activity level (recent content)

Then segments creators into A/B/C categories based on content signals.
Also enriches each profile with computed fields (engagement estimate, niche, email extraction).
"""

import re
import math
import logging
from datetime import datetime, timezone
from typing import Optional

from config import (
    FOLLOWER_MIN,
    FOLLOWER_MAX,
    SEGMENTS,
)

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
#  TASK 2 — FILTERING
# ─────────────────────────────────────────────────────────────────────────────

def is_india_based(profile: dict) -> bool:
    """
    Heuristic: check country code in stats, or Indian keywords in description.
    YouTube only returns country for channels that set it.
    """
    country = profile.get("country", "").upper()
    if country == "IN":
        return True

    # Fallback: scan description for India signals
    desc = (profile.get("description", "") + " " + profile.get("channel_keywords", "")).lower()
    india_signals = ["india", "indian", "भारत", "hindi", "cbse", "ncert", "rupee", "₹", "delhi", "mumbai", "bangalore", "hyderabad"]
    return any(sig in desc for sig in india_signals)


def is_active_recently(profile: dict, days_threshold: int = 60) -> bool:
    """
    Check if the creator has posted within the last `days_threshold` days.
    Uses recent_video_date if available, else channel published_at.
    """
    date_str = profile.get("recent_video_date") or profile.get("published_at", "")
    if not date_str:
        return True  # Give benefit of doubt if unknown

    try:
        # Parse ISO 8601 format from YouTube
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        delta_days = (now - dt).days
        return delta_days <= days_threshold
    except Exception:
        return True


def is_content_relevant(profile: dict, keywords: list[str]) -> bool:
    """
    Check if the channel's content is relevant to any of the discovery keywords.
    Scans: video titles, descriptions, channel description, channel keywords.
    """
    text_blob = " ".join([
        profile.get("video_title", ""),
        profile.get("video_description", ""),
        profile.get("description", ""),
        profile.get("channel_keywords", ""),
        profile.get("recent_video_title", ""),
        profile.get("recent_video_description", ""),
        profile.get("discovery_keyword", ""),
    ]).lower()

    return any(kw.lower() in text_blob for kw in keywords)


def filter_creators(profiles: list[dict], keywords: list[str]) -> list[dict]:
    """
    Apply all required filters and return only qualifying creators.
    """
    print("\n" + "═" * 60)
    print("  TASK 2 — AUTOMATED FILTERING & CLASSIFICATION")
    print("═" * 60)
    print(f"  Filters: {FOLLOWER_MIN:,}–{FOLLOWER_MAX:,} subscribers | India | Active | Relevant\n")

    passed = []
    reasons = {"follower_range": 0, "region": 0, "relevance": 0, "activity": 0}

    for p in profiles:
        subs = p.get("subscriber_count", 0)

        if not (FOLLOWER_MIN <= subs <= FOLLOWER_MAX):
            reasons["follower_range"] += 1
            continue

        if not is_india_based(p):
            reasons["region"] += 1
            continue

        if not is_content_relevant(p, keywords):
            reasons["relevance"] += 1
            continue

        if not is_active_recently(p):
            reasons["activity"] += 1
            continue

        passed.append(p)

    print(f"  Input     : {len(profiles)} creators")
    print(f"  ✗ Filtered: {reasons['follower_range']} (follower range) | "
          f"{reasons['region']} (region) | "
          f"{reasons['relevance']} (relevance) | "
          f"{reasons['activity']} (activity)")
    print(f"  ✓ Passed  : {len(passed)} creators\n")
    return passed


# ─────────────────────────────────────────────────────────────────────────────
#  TASK 2 — SEGMENTATION (automated, signal-based)
# ─────────────────────────────────────────────────────────────────────────────

def assign_segment(profile: dict, industry: str) -> tuple[str, str]:
    """
    Automatically classify a creator into segment A, B, or C
    based on content signals (titles, descriptions, keywords).

    Returns: (segment_key, segment_label)
    """
    industry_segments = SEGMENTS.get(industry, SEGMENTS["education"])

    text_blob = " ".join([
        profile.get("video_title", ""),
        profile.get("video_description", ""),
        profile.get("recent_video_title", ""),
        profile.get("recent_video_description", ""),
        profile.get("description", ""),
        profile.get("channel_keywords", ""),
        profile.get("discovery_keyword", ""),
    ]).lower()

    scores = {}
    for seg_key, seg_data in industry_segments.items():
        score = sum(1 for kw in seg_data["keywords"] if kw.lower() in text_blob)
        scores[seg_key] = score

    # Pick highest-scoring segment; default to C if tie/zero
    best = max(scores, key=lambda k: scores[k]) if any(v > 0 for v in scores.values()) else "C"
    label = industry_segments[best]["label"]
    return best, label


# ─────────────────────────────────────────────────────────────────────────────
#  TASK 3 — PROFILE ENRICHMENT
# ─────────────────────────────────────────────────────────────────────────────

def estimate_engagement_rate(subscriber_count: int, view_count: int, video_count: int) -> float:
    """
    Estimate engagement rate using average views per video vs subscribers.
    Formula: (avg_views / subscribers) × 100
    Industry standard: 2–5% is healthy for YouTube micro-influencers.
    """
    if subscriber_count == 0 or video_count == 0:
        return 0.0
    avg_views = view_count / video_count
    rate = (avg_views / subscriber_count) * 100
    return round(min(rate, 100.0), 2)  # cap at 100


def extract_email_from_bio(bio: str) -> Optional[str]:
    """
    Extract contact email from channel description using regex.
    Many Indian creators list business emails in their bio.
    """
    if not bio:
        return None
    pattern = r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"
    matches = re.findall(pattern, bio)
    # Filter out common placeholder/spam patterns
    for email in matches:
        if not any(bad in email.lower() for bad in ["example", "test@", "noreply", "support@youtube"]):
            return email
    return None


def extract_content_themes(profile: dict) -> list[str]:
    """
    Extract dominant content themes from available text signals.
    Returns up to 5 inferred themes.
    """
    text = " ".join([
        profile.get("video_title", ""),
        profile.get("recent_video_title", ""),
        profile.get("description", ""),
        profile.get("channel_keywords", ""),
    ]).lower()

    theme_map = {
        "Olympiad Preparation":  ["olympiad", "imo", "sof", "ntse", "competition"],
        "CBSE Board Prep":       ["cbse", "board exam", "class 10", "class 12", "ncert"],
        "Math & Reasoning":      ["math", "maths", "reasoning", "aptitude", "arithmetic"],
        "Science Education":     ["science", "physics", "chemistry", "biology"],
        "Student Competitions":  ["competition", "championship", "talent", "scholarship"],
        "Skincare & Beauty":     ["skincare", "skin", "moisturiser", "serum", "dermatologist"],
        "Makeup Tutorials":      ["makeup", "tutorial", "look", "eyeshadow", "foundation"],
        "Personal Finance":      ["finance", "investing", "sip", "mutual fund", "stocks"],
        "Budgeting & Savings":   ["budget", "savings", "money", "frugal"],
        "Product Reviews":       ["review", "unboxing", "haul", "worth it", "honest"],
        "Lifestyle":             ["lifestyle", "vlog", "daily", "routine", "day in"],
    }

    detected = [theme for theme, signals in theme_map.items() if any(s in text for s in signals)]
    return detected[:5] if detected else ["General Education"]


def days_since(date_str: str) -> Optional[int]:
    if not date_str:
        return None
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - dt).days
    except Exception:
        return None


def enrich_profile(profile: dict, industry: str) -> dict:
    """
    Enrich a filtered creator profile with computed fields.
    Returns the final structured creator object (Task 3 output).
    """
    subs = profile.get("subscriber_count", 0)
    views = profile.get("view_count", 0)
    videos = profile.get("video_count", 0)
    bio = profile.get("description", "")

    engagement = estimate_engagement_rate(subs, views, videos)
    email = extract_email_from_bio(bio)
    themes = extract_content_themes(profile)
    segment_key, segment_label = assign_segment(profile, industry)

    recent_days = days_since(profile.get("recent_video_date", ""))

    return {
        # ── Identity ─────────────────────────────────────────────────────────
        "channel_id":         profile.get("channel_id", ""),
        "channel_name":       profile.get("channel_title", "Unknown"),
        "platform":           "YouTube",
        "profile_url":        profile.get("profile_url", ""),
        "custom_url":         profile.get("custom_url", ""),
        "thumbnail":          profile.get("thumbnail", ""),

        # ── Metrics ──────────────────────────────────────────────────────────
        "subscriber_count":   subs,
        "total_views":        views,
        "video_count":        videos,
        "engagement_rate_pct": engagement,

        # ── Content signals ───────────────────────────────────────────────────
        "content_themes":     themes,
        "niche_classification": segment_label,
        "segment":            segment_key,
        "discovery_keyword":  profile.get("discovery_keyword", ""),
        "recent_video_title": profile.get("recent_video_title", "N/A"),
        "recent_video_date":  profile.get("recent_video_date", "N/A"),
        "days_since_last_post": recent_days,

        # ── Contact ───────────────────────────────────────────────────────────
        "contact_email":      email,

        # ── Raw bio (for outreach generator) ─────────────────────────────────
        "bio_snippet":        bio[:300].strip(),
        "industry":           industry,
    }


def filter_and_enrich(profiles: list[dict], keywords: list[str], industry: str) -> list[dict]:
    """
    Combined Task 2 + Task 3 pipeline stage.
    Filters creators, segments them, and enriches each profile.
    """
    # Task 2 — Filter
    filtered = filter_creators(profiles, keywords)

    # Task 3 — Enrich
    print("  TASK 3 — PROFILE ENRICHMENT ENGINE")
    print("═" * 60)
    enriched = []
    for p in filtered:
        enriched.append(enrich_profile(p, industry))

    # Summary by segment
    from collections import Counter
    seg_counts = Counter(e["segment"] for e in enriched)
    print(f"  Enriched {len(enriched)} profiles:")
    for seg, count in sorted(seg_counts.items()):
        label = SEGMENTS.get(industry, {}).get(seg, {}).get("label", seg)
        print(f"    Segment {seg} ({label}): {count} creators")
    print()

    return enriched