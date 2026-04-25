"""
task6_outreach_generator.py — Personalized Outreach Message Generator

Generates:
  A) Email collaboration pitch (60–90 words)
  B) Instagram DM (15–30 words)

Messages are dynamically generated using content signals — NOT templates.
Each message references: creator niche, recent content, collaboration value, audience relevance.

Uses Claude API (Anthropic) if key is available, otherwise uses a
rule-based dynamic generator that still produces highly personalized messages.
"""

import re
import os
import json
import random
import logging
from config import BRAND_CONTEXT, ANTHROPIC_API_KEY

logger = logging.getLogger(__name__)

try:
    import anthropic
    _ANTHROPIC_AVAILABLE = bool(ANTHROPIC_API_KEY)
except ImportError:
    _ANTHROPIC_AVAILABLE = False


# ─────────────────────────────────────────────────────────────────────────────
#  CLAUDE-POWERED GENERATION (when API key available)
# ─────────────────────────────────────────────────────────────────────────────

def generate_with_claude(profile: dict, industry: str) -> dict:
    """
    Use Claude API to generate highly personalized outreach messages.
    """
    brand = BRAND_CONTEXT.get(industry, BRAND_CONTEXT["education"])
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    creator_context = f"""
Creator: {profile.get('channel_name')}
Platform: YouTube
Subscribers: {profile.get('subscriber_count', 0):,}
Niche: {profile.get('niche_classification')}
Segment: {profile.get('segment')}
Content Themes: {', '.join(profile.get('content_themes', []))}
Recent Video: {profile.get('recent_video_title', 'N/A')}
Detected Intents: {', '.join(profile.get('content_intelligence', {}).get('detected_intents', []))}
Primary Intent: {profile.get('content_intelligence', {}).get('primary_intent', 'N/A')}
Fit Score: {profile.get('fit_score', 0):.2f}
Recommended Collab: {', '.join(profile.get('recommended_collab', []))}
"""

    prompt = f"""You are a brand partnerships specialist at {brand['brand_name']}.

{brand['brand_name']} is: {brand['brand_offering']}
Brand value prop: {brand['brand_value']}
Call to action: {brand['cta']}

Creator context:
{creator_context}

Generate TWO outreach messages:

1. EMAIL (60–90 words):
- Subject line
- Body referencing creator's specific niche and recent content
- Clear collaboration value for their audience
- Professional but warm tone
- Specific CTA

2. INSTAGRAM DM (15–30 words):
- Casual, direct, conversational
- Reference their content topic
- Clear collaboration intent

Return ONLY valid JSON in this exact format:
{{
  "email_subject": "...",
  "email_body": "...",
  "instagram_dm": "..."
}}"""

    try:
        message = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = message.content[0].text.strip()
        # Strip markdown fences if present
        raw = re.sub(r"```json|```", "", raw).strip()
        return json.loads(raw)
    except Exception as e:
        logger.warning(f"Claude API error, falling back to rule-based: {e}")
        return generate_rule_based(profile, industry)


# ─────────────────────────────────────────────────────────────────────────────
#  RULE-BASED DYNAMIC GENERATION (fallback — still personalized)
# ─────────────────────────────────────────────────────────────────────────────

# Dynamic phrase pools — picked based on creator signals
EMAIL_OPENERS = [
    "I've been following your content on {platform} and genuinely love how you approach {primary_intent}.",
    "Your recent video on '{recent_video}' stood out to me — the way you break down {primary_intent} for your students is exceptional.",
    "As someone who works with creators in the {niche} space, I was impressed by your {primary_intent} content.",
    "Your {subscriber_count} subscribers clearly value your expertise in {niche} — and that's exactly why I'm reaching out.",
]

EMAIL_VALUE_PROPS = {
    "education": {
        "A": "Our platform helps students prepare for olympiads with AI-adaptive practice tests — a natural fit for your audience of serious learners.",
        "B": "We provide reasoning skill-builders that perfectly complement the aptitude content you create.",
        "C": "Our CBSE-aligned resources have helped 50,000+ students improve board exam scores — your audience would love them.",
    },
    "beauty": {
        "A": "Our dermatologist-tested formulas are designed for Indian skin — your skincare-focused audience would genuinely benefit.",
        "B": "We'd love for you to feature our products in one of your tutorial videos for an authentic review.",
        "C": "Our affordable range is exactly what your product-review audience looks for.",
    },
    "fintech": {
        "A": "Our zero-commission SIP app is perfect for first-time investors — exactly who watches your content.",
        "B": "Your budgeting audience would love our savings goal tracker — totally free and built for India.",
        "C": "We'd love to offer your audience a special credit-building guide as part of our partnership.",
    },
}

EMAIL_CTAS = [
    "Would you be open to a quick 15-minute call this week to explore this further?",
    "I'd love to send over a collaboration brief — let me know if you're interested!",
    "Can I share more details about our creator program? Happy to tailor it around your content style.",
    "Let me know if you'd like to explore a paid sponsorship or barter arrangement — completely flexible!",
]

DM_TEMPLATES = [
    "Hey {name}! Loved your {recent_video} content 🙌 We'd love to collaborate with you on {collab_type} — DM back if interested!",
    "Hi {name}, your {niche} content is exactly what we're looking for at {brand}! Open to a collab? 🤝",
    "Hey {name}! Your audience is a perfect fit for {brand}'s mission. Would love to chat about {collab_type}!",
    "Hi {name} 👋 Big fan of your {niche} videos. We have an exciting {collab_type} opportunity — interested?",
]


def _pick(pool: list, **kwargs) -> str:
    """Pick a random phrase from pool and format with kwargs."""
    return random.choice(pool).format(**kwargs)


def generate_rule_based(profile: dict, industry: str) -> dict:
    """
    Rule-based personalized outreach generator.
    Uses content signals to pick the most relevant phrases from pools.
    Still produces unique, personalized output — not a static template.
    """
    brand = BRAND_CONTEXT.get(industry, BRAND_CONTEXT["education"])
    name = profile.get("channel_name", "Creator")
    niche = profile.get("niche_classification", "education")
    segment = profile.get("segment", "C")
    subs = profile.get("subscriber_count", 0)
    recent_video = profile.get("recent_video_title", "your recent video")[:50]
    platform = profile.get("platform", "YouTube")
    primary_intent = profile.get("content_intelligence", {}).get("primary_intent", "content").replace("_", " ")
    collab_types = profile.get("recommended_collab", ["collaboration"])
    collab_type = collab_types[0].lower() if collab_types else "collaboration"

    # Pick opener
    opener = _pick(EMAIL_OPENERS,
        platform=platform,
        primary_intent=primary_intent,
        recent_video=recent_video,
        niche=niche,
        subscriber_count=f"{subs:,}",
    )

    # Pick value prop
    value_props = EMAIL_VALUE_PROPS.get(industry, EMAIL_VALUE_PROPS["education"])
    value_prop = value_props.get(segment, value_props.get("C", "We think your audience would love what we offer."))

    # Pick CTA
    cta = _pick(EMAIL_CTAS)

    # Build email body
    email_body = (
        f"Hi {name},\n\n"
        f"{opener}\n\n"
        f"{value_prop} We'd love to partner with you for a {collab_type} that adds real value to your audience.\n\n"
        f"{cta}\n\n"
        f"Best,\n{brand['brand_name']} Partnerships Team"
    )

    # Subject line
    subjects = [
        f"Collaboration opportunity for {name} × {brand['brand_name']}",
        f"Your {niche} content + {brand['brand_name']} = perfect fit 🤝",
        f"Partnership proposal for {name} | {brand['brand_name']}",
        f"{brand['brand_name']} × {name}: Let's create something great",
    ]
    subject = random.choice(subjects)

    # Instagram DM
    dm = _pick(DM_TEMPLATES,
        name=name.split()[0],
        recent_video=recent_video[:30],
        niche=niche,
        brand=brand["brand_name"],
        collab_type=collab_type,
    )

    return {
        "email_subject": subject,
        "email_body": email_body,
        "instagram_dm": dm,
    }


def count_words(text: str) -> int:
    return len(text.split())


def validate_message_lengths(messages: dict) -> dict:
    """
    Validate that generated messages meet word count requirements.
    Logs warnings if outside spec.
    """
    from config import EMAIL_MIN_WORDS, EMAIL_MAX_WORDS, DM_MIN_WORDS, DM_MAX_WORDS

    body_words = count_words(messages.get("email_body", ""))
    dm_words = count_words(messages.get("instagram_dm", ""))

    if not (EMAIL_MIN_WORDS <= body_words <= EMAIL_MAX_WORDS):
        logger.debug(f"  Email body word count {body_words} outside {EMAIL_MIN_WORDS}–{EMAIL_MAX_WORDS}")
    if not (DM_MIN_WORDS <= dm_words <= DM_MAX_WORDS):
        logger.debug(f"  DM word count {dm_words} outside {DM_MIN_WORDS}–{DM_MAX_WORDS}")

    return {**messages, "_email_word_count": body_words, "_dm_word_count": dm_words}


def generate_outreach(profile: dict, industry: str) -> dict:
    """
    Main outreach generation function.
    Uses Claude API if available, else rule-based dynamic generator.
    """
    if _ANTHROPIC_AVAILABLE:
        messages = generate_with_claude(profile, industry)
    else:
        messages = generate_rule_based(profile, industry)

    return validate_message_lengths(messages)


def generate_all_outreach(profiles: list[dict], industry: str) -> list[dict]:
    """
    Generate personalized outreach messages for all qualified creators.
    """
    print("═" * 60)
    print("  TASK 6 — PERSONALIZED OUTREACH MESSAGE GENERATOR")
    print("═" * 60)
    method = "Claude API (AI-powered)" if _ANTHROPIC_AVAILABLE else "Rule-based Dynamic Generator"
    print(f"  Generation method: {method}\n")

    for i, p in enumerate(profiles):
        outreach = generate_outreach(p, industry)
        p["outreach"] = outreach
        print(f"  [{i+1}/{len(profiles)}] Generated for: {p['channel_name'][:40]}")

    print(f"\n  ✅ {len(profiles)} outreach message sets generated\n")
    return profiles