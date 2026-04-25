"""
task9_collab_strategy.py — Collaboration Strategy Layer + Output Generation

Task 9: Maps creator segments to collaboration strategies.
Also handles:
  - JSON output of enriched creators (deliverable format)
  - Console report (tabulated)
  - Sample outreach message display
"""

import json
from pathlib import Path
from datetime import datetime
from config import COLLAB_STRATEGIES, SEGMENTS, BRAND_CONTEXT

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
#  TASK 9 — COLLABORATION STRATEGY
# ─────────────────────────────────────────────────────────────────────────────

COLLAB_DETAILS = {
    "Paid Sponsorship": {
        "description": "Fixed-fee brand mention in video",
        "typical_rate_inr": "₹5,000–₹25,000 per video for micro-influencers",
        "deliverable": "30–60 sec brand mention + product demo",
        "best_for": "High-fit score creators (Grade A)",
    },
    "Affiliate Program": {
        "description": "Commission-based link sharing",
        "typical_rate_inr": "5–15% commission per sale",
        "deliverable": "Custom promo code + tracking link in video description",
        "best_for": "Finance/EdTech creators with high-intent audiences",
    },
    "Barter Collaboration": {
        "description": "Free product/service in exchange for review",
        "typical_rate_inr": "Product cost only (no cash)",
        "deliverable": "Honest review video or Instagram story",
        "best_for": "New creators (Segment C) or trial campaigns",
    },
    "UGC Partnerships": {
        "description": "Creator produces content owned by brand",
        "typical_rate_inr": "₹2,000–₹10,000 per asset",
        "deliverable": "Short video/reel for brand's own channels",
        "best_for": "Creators with strong visual content style",
    },
    "Product Trials": {
        "description": "Send product for organic review (no obligation)",
        "typical_rate_inr": "Product cost only",
        "deliverable": "Organic mention if creator likes it",
        "best_for": "Building authentic brand–creator relationships",
    },
    "Ambassador Program": {
        "description": "Long-term brand representation",
        "typical_rate_inr": "Monthly retainer ₹10,000–₹50,000",
        "deliverable": "Regular content, events, community engagement",
        "best_for": "Grade A creators with highly aligned audience",
    },
    "Assessment Ecosystem Partnership": {
        "description": "Deep integration — creator uses brand platform in content",
        "typical_rate_inr": "Revenue share or premium retainer",
        "deliverable": "Tutorial series, live practice sessions on platform",
        "best_for": "Education platform + olympiad preparation creators",
    },
}


def recommend_collab_strategy(profile: dict, industry: str) -> dict:
    """
    Return detailed collaboration strategy recommendation for a creator.
    """
    segment  = profile.get("segment", "C")
    fit_grade = profile.get("fit_grade", "C")

    strategies = COLLAB_STRATEGIES.get(industry, {}).get(segment, ["Barter Collaboration"])

    # Grade A → lead with paid, Grade B → affiliate first, Grade C → barter/UGC first
    if fit_grade == "A":
        priority_order = ["Paid Sponsorship", "Ambassador Program"] + strategies
    elif fit_grade == "B":
        priority_order = ["Affiliate Program"] + strategies
    else:
        priority_order = ["Barter Collaboration", "Product Trials"] + strategies

    # Deduplicate while preserving order
    seen = set()
    ordered = []
    for s in priority_order:
        if s not in seen:
            seen.add(s)
            ordered.append(s)

    top_strategy = ordered[0]
    details = COLLAB_DETAILS.get(top_strategy, {})

    return {
        "primary_strategy":    top_strategy,
        "all_strategies":      ordered[:3],
        "strategy_details":    details,
        "fit_rationale":       f"Grade {fit_grade} fit score {profile.get('fit_score', 0):.2f} → {top_strategy}",
    }


def apply_collab_strategies(profiles: list[dict], industry: str) -> list[dict]:
    """Apply collaboration strategy recommendations to all profiles."""
    print("═" * 60)
    print("  TASK 9 — COLLABORATION STRATEGY LAYER")
    print("═" * 60)

    strategy_counts = {}
    for p in profiles:
        strategy = recommend_collab_strategy(p, industry)
        p["collab_strategy"] = strategy
        s = strategy["primary_strategy"]
        strategy_counts[s] = strategy_counts.get(s, 0) + 1

    print(f"  Strategy distribution across {len(profiles)} creators:")
    for strat, count in sorted(strategy_counts.items(), key=lambda x: -x[1]):
        print(f"    {strat}: {count} creators")
    print()
    return profiles


# ─────────────────────────────────────────────────────────────────────────────
#  OUTPUT — JSON export
# ─────────────────────────────────────────────────────────────────────────────

def export_enriched_creators(profiles: list[dict], industry: str) -> Path:
    """
    Export final enriched creator profiles as JSON.
    This is the 'Sample enriched creator output format' deliverable.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = OUTPUT_DIR / f"enriched_creators_{industry}_{timestamp}.json"

    # Build clean output schema (Task 3 minimum fields + all enrichments)
    output = []
    for p in profiles:
        record = {
            # ── Task 3 required fields ────────────────────────────────────────
            "platform":           p.get("platform"),
            "channel_name":       p.get("channel_name"),
            "profile_url":        p.get("profile_url"),
            "subscriber_count":   p.get("subscriber_count"),
            "engagement_rate_pct": p.get("engagement_rate_pct"),
            "content_themes":     p.get("content_themes"),
            "niche_classification": p.get("niche_classification"),
            "contact_email":      p.get("contact_email"),

            # ── Segmentation ──────────────────────────────────────────────────
            "segment":            p.get("segment"),
            "segment_label":      p.get("niche_classification"),

            # ── Content intelligence ──────────────────────────────────────────
            "detected_intents":   p.get("content_intelligence", {}).get("detected_intents"),
            "primary_intent":     p.get("content_intelligence", {}).get("primary_intent"),
            "signal_strength":    p.get("content_intelligence", {}).get("content_signal_strength"),

            # ── Brand fit ─────────────────────────────────────────────────────
            "fit_score":          p.get("fit_score"),
            "fit_grade":          p.get("fit_grade"),
            "component_scores":   p.get("component_scores"),

            # ── Collaboration ─────────────────────────────────────────────────
            "primary_collab_strategy": p.get("collab_strategy", {}).get("primary_strategy"),
            "all_strategies":         p.get("collab_strategy", {}).get("all_strategies"),

            # ── Outreach messages ─────────────────────────────────────────────
            "outreach": {
                "email_subject":   p.get("outreach", {}).get("email_subject"),
                "email_body":      p.get("outreach", {}).get("email_body"),
                "email_word_count": p.get("outreach", {}).get("_email_word_count"),
                "instagram_dm":    p.get("outreach", {}).get("instagram_dm"),
                "dm_word_count":   p.get("outreach", {}).get("_dm_word_count"),
            },

            # ── Activity ──────────────────────────────────────────────────────
            "recent_video_title": p.get("recent_video_title"),
            "recent_video_date":  p.get("recent_video_date"),
            "days_since_last_post": p.get("days_since_last_post"),
        }
        output.append(record)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    return path


# ─────────────────────────────────────────────────────────────────────────────
#  CONSOLE REPORT
# ─────────────────────────────────────────────────────────────────────────────

def print_final_report(profiles: list[dict], industry: str):
    """Print a formatted console summary of the pipeline results."""
    brand = BRAND_CONTEXT.get(industry, BRAND_CONTEXT["education"])

    print("\n" + "╔" + "═" * 62 + "╗")
    print("║" + f"  FINAL REPORT — {brand['brand_name']} Micro-Influencer Pipeline".center(62) + "║")
    print("╠" + "═" * 62 + "╣")
    print(f"║  Industry   : {industry.upper():<48}║")
    print(f"║  Total qualified creators : {len(profiles):<34}║")
    print("╠" + "═" * 62 + "╣")

    for i, p in enumerate(profiles[:10], 1):   # show top 10
        name      = p.get("channel_name", "Unknown")[:28]
        subs      = p.get("subscriber_count", 0)
        eng       = p.get("engagement_rate_pct", 0)
        seg       = p.get("segment", "?")
        score     = p.get("fit_score", 0)
        grade     = p.get("fit_grade", "?")
        strategy  = p.get("collab_strategy", {}).get("primary_strategy", "N/A")[:22]
        email     = "✓" if p.get("contact_email") else "✗"

        print(f"║  {i:2}. {name:<28} | {subs:>7,} subs | Seg {seg} | {score:.2f} [{grade}] ║")
        print(f"║      📧 {email} | Eng {eng:.1f}% | {strategy:<30}║")
        print("║" + "─" * 62 + "║")

    if len(profiles) > 10:
        print(f"║  ... and {len(profiles)-10} more creators in JSON output{' ' * 19}║")

    print("╚" + "═" * 62 + "╝")

    # Show sample outreach for top creator
    if profiles:
        top = profiles[0]
        outreach = top.get("outreach", {})
        print(f"\n{'─'*64}")
        print(f"  SAMPLE OUTREACH — {top.get('channel_name')}")
        print(f"{'─'*64}")
        print(f"\n  📧 EMAIL SUBJECT:\n  {outreach.get('email_subject')}")
        print(f"\n  📧 EMAIL BODY ({outreach.get('_email_word_count', '?')} words):")
        for line in outreach.get("email_body", "").split("\n"):
            print(f"  {line}")
        print(f"\n  📱 INSTAGRAM DM ({outreach.get('_dm_word_count', '?')} words):")
        print(f"  {outreach.get('instagram_dm')}")
        print(f"{'─'*64}\n")