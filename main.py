"""
main.py — Micro-Influencer Outreach System Orchestrator
Runs the full 9-task pipeline end-to-end.

Usage:
    python main.py                          # interactive mode
    python main.py --industry education     # preset keywords
    python main.py --industry beauty
    python main.py --industry fintech
    python main.py --keywords "olympiad preparation" "CBSE math" --industry education
    python main.py --demo                   # full demo with mock data (no API key needed)
"""

import sys
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.WARNING,
    format="%(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ── Import pipeline stages ───────────────────────────────────────────────────
from config import YOUTUBE_API_KEY, SEGMENTS, BRAND_CONTEXT
from task2_filter_classify import filter_and_enrich
from task4_content_intelligence import analyze_and_score
from task6_outreach_generator import generate_all_outreach
from task7_outreach_automation import execute_outreach, WORKFLOW_EXPLANATION
from task9_collab_strategy import apply_collab_strategies, export_enriched_creators, print_final_report


# ─────────────────────────────────────────────────────────────────────────────
#  PRESET KEYWORDS per industry
# ─────────────────────────────────────────────────────────────────────────────

PRESET_KEYWORDS = {
    "education": [
        "olympiad preparation India",
        "CBSE math tricks",
        "student competitions India",
        "reasoning aptitude for students",
        "NTSE preparation",
        "science olympiad India",
        "math olympiad class 8",
    ],
    "beauty": [
        "skincare routine India",
        "affordable makeup India",
        "dermatologist skincare tips India",
        "Indian skin care tips",
        "makeup tutorial Hindi",
    ],
    "fintech": [
        "personal finance India",
        "SIP investing basics",
        "credit card hacks India",
        "mutual fund for beginners India",
        "budgeting tips India",
    ],
}


# ─────────────────────────────────────────────────────────────────────────────
#  DEMO MODE — Uses mock data so you can test without API key
# ─────────────────────────────────────────────────────────────────────────────

def generate_mock_profiles(industry: str, keywords: list[str]) -> list[dict]:
    """
    Generate realistic mock creator profiles for demo/testing.
    Simulates what the YouTube API discovery would return.
    """
    import random

    mock_creators = [
        # Education creators
        {"name": "OlympiadGuru", "subs": 42000, "seg": "A", "kw": "olympiad preparation India",
         "video": "IMO 2024 Preparation Strategy for Class 8 Students | Complete Roadmap",
         "desc": "Teaching olympiad math to 40k+ students. For collaboration: olympiadguru@gmail.com",
         "themes": ["Olympiad Preparation", "Math & Reasoning"]},
        {"name": "CBSE Champion", "subs": 78000, "seg": "C", "kw": "CBSE math tricks",
         "video": "CBSE Class 10 Maths: Trigonometry Shortcuts That Actually Work!",
         "desc": "Making CBSE board exam prep easy and fun. Business: cbsechampion@gmail.com",
         "themes": ["CBSE Board Prep", "Math & Reasoning"]},
        {"name": "ReasoningMaster", "subs": 23000, "seg": "B", "kw": "reasoning aptitude for students",
         "video": "Top 20 Reasoning Questions for NTSE 2024 | With Tricks",
         "desc": "Aptitude and reasoning for competitive exams. Contact: reasoningmaster.in@gmail.com",
         "themes": ["Math & Reasoning", "Olympiad Preparation"]},
        {"name": "ScienceOlympics", "subs": 15000, "seg": "A", "kw": "science olympiad India",
         "video": "NSO 2024: Biology Questions Every Student Gets Wrong",
         "desc": "Science Olympiad prep channel. NSO, SOF, Silverzone specialist.",
         "themes": ["Olympiad Preparation", "Science Education"]},
        {"name": "StudentSuccess", "subs": 56000, "seg": "C", "kw": "student competitions India",
         "video": "Top 10 National Level Competitions for School Students 2024",
         "desc": "Helping Indian students discover the right competitions. DM for collab!",
         "themes": ["Student Competitions", "Olympiad Preparation"]},
        {"name": "MathWizard India", "subs": 91000, "seg": "B", "kw": "CBSE math tricks",
         "video": "Mental Math Tricks: Multiply Any 2-Digit Numbers in 3 Seconds",
         "desc": "Math tricks, olympiad prep, aptitude. Business email: mathwizardindia@gmail.com",
         "themes": ["Math & Reasoning", "CBSE Board Prep"]},
        {"name": "CompetitiveKids", "subs": 8500, "seg": "A", "kw": "olympiad preparation India",
         "video": "IMO Gold Medalist Shares His 6-Month Study Plan",
         "desc": "Inspiring the next generation of olympiad champions. Contact via YouTube.",
         "themes": ["Olympiad Preparation", "Student Competitions"]},
        {"name": "ExamCracker",  "subs": 34000, "seg": "C", "kw": "NTSE preparation",
         "video": "NTSE Stage 1: Last 10 Years SAT Paper Analysis",
         "desc": "NTSE, scholarship exams, board prep. examcracker@outlook.com",
         "themes": ["Student Competitions", "CBSE Board Prep"]},
    ]

    profiles = []
    for i, c in enumerate(mock_creators):
        subs = c["subs"]
        views = subs * random.randint(80, 300)
        videos = random.randint(50, 400)

        # Use a recent date within the last 30 days
        from datetime import datetime, timezone, timedelta
        recent_date = (datetime.now(timezone.utc) - timedelta(days=random.randint(3, 28))).strftime("%Y-%m-%dT%H:%M:%SZ")

        profiles.append({
            "channel_id":          f"UC_mock_{i:04d}",
            "channel_title":       c["name"],
            "video_title":         c["video"],
            "video_description":   c["desc"],
            "published_at":        "2020-01-15T00:00:00Z",
            "discovery_keyword":   c["kw"],
            "subscriber_count":    subs,
            "view_count":          views,
            "video_count":         videos,
            "country":             "IN",
            "description":         c["desc"],
            "custom_url":          f"@{c['name'].replace(' ', '').lower()}",
            "channel_keywords":    " ".join(c.get("themes", [])),
            "thumbnail":           "",
            "recent_video_title":  c["video"],
            "recent_video_description": c["desc"],
            "recent_video_date":   recent_date,
            "recent_video_id":     f"vid_mock_{i:04d}",
            "profile_url":         f"https://www.youtube.com/channel/UC_mock_{i:04d}",
            "platform":            "YouTube",
        })

    return profiles


# ─────────────────────────────────────────────────────────────────────────────
#  PIPELINE RUNNER
# ─────────────────────────────────────────────────────────────────────────────

def run_pipeline(keywords: list[str], industry: str, demo_mode: bool = False) -> list[dict]:
    """
    Execute the full 9-task pipeline.

    Returns:
        Final list of enriched, scored, outreach-ready creator profiles.
    """
    print("\n" + "╔" + "═" * 62 + "╗")
    print("║" + "  MICRO-INFLUENCER OUTREACH SYSTEM — PIPELINE START".center(62) + "║")
    print("║" + f"  Industry: {industry.upper()} | Mode: {'DEMO' if demo_mode else 'LIVE'}".center(62) + "║")
    print("╚" + "═" * 62 + "╝\n")

    # ── TASK 1: Discovery ────────────────────────────────────────────────────
    if demo_mode:
        print("═" * 60)
        print("  TASK 1 — REAL-TIME INFLUENCER DISCOVERY (DEMO MODE)")
        print("═" * 60)
        print("  [Demo] Using mock creator data — set YOUTUBE_API_KEY to use live API\n")
        raw_profiles = generate_mock_profiles(industry, keywords)
        print(f"  ✅ {len(raw_profiles)} mock profiles generated\n")
    else:
        from task1_discovery import discover_influencers
        raw_profiles = discover_influencers(keywords)

    if not raw_profiles:
        print("  ⚠️  No profiles discovered. Check API key or try different keywords.")
        return []

    # ── TASKS 2+3: Filter + Enrich ───────────────────────────────────────────
    enriched = filter_and_enrich(raw_profiles, keywords, industry)

    if not enriched:
        print("  ⚠️  No creators passed filtering. Try relaxing keyword constraints.")
        return []

    # ── TASKS 4+5: Content Intelligence + Brand-Fit Scoring ─────────────────
    scored = analyze_and_score(enriched, industry)

    if not scored:
        print("  ⚠️  No creators met the brand-fit threshold.")
        return []

    # ── TASK 6: Generate Outreach Messages ───────────────────────────────────
    with_outreach = generate_all_outreach(scored, industry)

    # ── TASK 7: Automation Layer ─────────────────────────────────────────────
    execute_outreach(with_outreach, industry, live_mode=False)

    # ── TASK 9: Collaboration Strategies ─────────────────────────────────────
    final = apply_collab_strategies(with_outreach, industry)

    # ── OUTPUT ───────────────────────────────────────────────────────────────
    json_path = export_enriched_creators(final, industry)
    print(f"  💾 Enriched creator JSON saved: {json_path}")

    # ── CONSOLE REPORT ───────────────────────────────────────────────────────
    print_final_report(final, industry)

    # ── ARCHITECTURE DIAGRAM ─────────────────────────────────────────────────
    print(WORKFLOW_EXPLANATION)

    return final


# ─────────────────────────────────────────────────────────────────────────────
#  CLI INTERFACE
# ─────────────────────────────────────────────────────────────────────────────

def interactive_mode():
    """Run in interactive mode — prompt for industry and keywords."""
    print("\n  ┌─────────────────────────────────────────────┐")
    print("  │   MICRO-INFLUENCER OUTREACH SYSTEM v1.0     │")
    print("  └─────────────────────────────────────────────┘\n")

    print("  Available industries: education, beauty, fintech")
    industry = input("  Enter industry (or press Enter for 'education'): ").strip().lower()
    if not industry:
        industry = "education"
    if industry not in PRESET_KEYWORDS:
        print(f"  ⚠️  Unknown industry '{industry}', defaulting to 'education'")
        industry = "education"

    print(f"\n  Preset keywords for {industry}:")
    for i, kw in enumerate(PRESET_KEYWORDS[industry], 1):
        print(f"    {i}. {kw}")

    use_preset = input("\n  Use preset keywords? [Y/n]: ").strip().lower()
    if use_preset in ("n", "no"):
        raw = input("  Enter custom keywords (comma-separated): ")
        keywords = [k.strip() for k in raw.split(",") if k.strip()]
    else:
        keywords = PRESET_KEYWORDS[industry]

    demo = YOUTUBE_API_KEY == "YOUR_YOUTUBE_API_KEY_HERE"
    if demo:
        print("\n  ⚠️  No YouTube API key found in .env — running in DEMO mode with mock data.")
        print("     Set YOUTUBE_API_KEY=your_key in .env to use live YouTube discovery.\n")

    return keywords, industry, demo


def main():
    parser = argparse.ArgumentParser(
        description="Real-Time Micro-Influencer Outreach System",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("--industry", choices=["education", "beauty", "fintech"],
                        help="Brand industry context")
    parser.add_argument("--keywords", nargs="+",
                        help="Custom discovery keywords")
    parser.add_argument("--demo", action="store_true",
                        help="Run in demo mode with mock data (no API key needed)")
    parser.add_argument("--no-interactive", action="store_true",
                        help="Skip interactive prompts, use defaults")

    args = parser.parse_args()

    if args.industry or args.no_interactive:
        industry = args.industry or "education"
        keywords = args.keywords or PRESET_KEYWORDS[industry]
        demo     = args.demo or YOUTUBE_API_KEY == "YOUR_YOUTUBE_API_KEY_HERE"
    else:
        keywords, industry, demo = interactive_mode()

    run_pipeline(keywords, industry, demo_mode=demo)


if __name__ == "__main__":
    main()