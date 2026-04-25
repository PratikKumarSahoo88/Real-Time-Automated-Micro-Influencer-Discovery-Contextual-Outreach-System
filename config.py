"""
config.py — Central configuration for the Micro-Influencer Outreach System
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── API Keys (set in .env or environment) ─────────────────────────────────────
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "YOUR_YOUTUBE_API_KEY_HERE")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")   # optional — enriches messages

# ── Discovery Filters ─────────────────────────────────────────────────────────
FOLLOWER_MIN = 5_000
FOLLOWER_MAX = 100_000
TARGET_REGION = "IN"          # ISO 3166-1 alpha-2 country code

# ── YouTube Search Config ─────────────────────────────────────────────────────
YT_MAX_RESULTS_PER_KEYWORD = 10   # per keyword query
YT_MIN_VIEW_COUNT = 1_000         # discard very low-view channels
YT_RELEVANCE_LANGUAGE = "hi"      # Hindi preferred; also returns English

# ── Brand–Fit Score Weights ───────────────────────────────────────────────────
FIT_WEIGHT_KEYWORD_MATCH   = 0.40
FIT_WEIGHT_SEGMENT_ALIGN   = 0.30
FIT_WEIGHT_ENGAGEMENT_RATE = 0.20
FIT_WEIGHT_RECENCY         = 0.10
FIT_SCORE_THRESHOLD        = 0.50   # minimum to include in outreach list

# ── Outreach Message Config ───────────────────────────────────────────────────
EMAIL_MIN_WORDS = 60
EMAIL_MAX_WORDS = 90
DM_MIN_WORDS    = 15
DM_MAX_WORDS    = 30

# ── Segmentation definitions per industry ─────────────────────────────────────
SEGMENTS = {
    "education": {
        "A": {
            "label": "Olympiad & Competitive Prep",
            "keywords": ["olympiad", "competition", "competitive exam", "scholarship", "NTSE", "IMO", "SOF"],
        },
        "B": {
            "label": "Reasoning & Aptitude",
            "keywords": ["reasoning", "aptitude", "logical", "puzzle", "brain", "IQ", "mental math"],
        },
        "C": {
            "label": "Curriculum & Board Prep",
            "keywords": ["CBSE", "ICSE", "board exam", "class 10", "class 12", "math tricks", "science class"],
        },
    },
    "beauty": {
        "A": {"label": "Skincare Educators",   "keywords": ["skincare", "dermatologist", "serum", "moisturiser"]},
        "B": {"label": "Makeup Tutorial",      "keywords": ["makeup", "tutorial", "eyeshadow", "lipstick", "foundation"]},
        "C": {"label": "Product Reviewers",    "keywords": ["review", "affordable", "haul", "unboxing", "worth it"]},
    },
    "fintech": {
        "A": {"label": "Investment Educators", "keywords": ["SIP", "mutual fund", "stock market", "investing"]},
        "B": {"label": "Budgeting Advisors",   "keywords": ["budget", "savings", "personal finance", "money management"]},
        "C": {"label": "Credit & Cards",       "keywords": ["credit card", "credit score", "loan", "EMI", "CIBIL"]},
    },
}

# ── Collaboration strategy map ─────────────────────────────────────────────────
COLLAB_STRATEGIES = {
    "education": {
        "A": ["Paid Sponsorship", "Assessment Ecosystem Partnership", "Ambassador Program"],
        "B": ["UGC Partnerships", "Barter Collaboration", "Affiliate Program"],
        "C": ["Product Trials", "Barter Collaboration", "Affiliate Program"],
    },
    "beauty": {
        "A": ["Product Trials", "Paid Sponsorship", "Ambassador Program"],
        "B": ["Paid Sponsorship", "UGC Partnerships", "Barter Collaboration"],
        "C": ["Affiliate Program", "Product Trials", "UGC Partnerships"],
    },
    "fintech": {
        "A": ["Affiliate Program", "Paid Sponsorship", "Ambassador Program"],
        "B": ["Affiliate Program", "Barter Collaboration", "UGC Partnerships"],
        "C": ["Affiliate Program", "Paid Sponsorship", "Product Trials"],
    },
}

# ── Brand context templates (used in outreach generation) ─────────────────────
BRAND_CONTEXT = {
    "education": {
        "brand_name": "SPARK Olympiads",
        "brand_offering": "India's fastest-growing competitive exam preparation platform for students in Classes 3–12",
        "brand_value": "Help students crack olympiads with AI-powered practice tests and adaptive learning paths",
        "cta": "feature your students' success stories on our platform",
    },
    "beauty": {
        "brand_name": "GlowLab India",
        "brand_offering": "affordable dermatologist-tested skincare range for Indian skin tones",
        "brand_value": "Give your audience science-backed skincare that actually works for Indian climate",
        "cta": "try our new Vitamin C range and share your honest review",
    },
    "fintech": {
        "brand_name": "WealthSeed",
        "brand_offering": "zero-commission SIP investing app for first-time investors",
        "brand_value": "Help your audience start their investment journey with just ₹100/month",
        "cta": "introduce your audience to smarter, simpler investing",
    },
}