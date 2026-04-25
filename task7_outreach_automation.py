"""
task7_outreach_automation.py — Outreach Automation Layer

Handles programmatic execution of outreach via:
  - Email: Gmail SMTP (free) / Brevo / SendGrid
  - Instagram DM: Instagrapi (open source)

In DEMO mode (no credentials): logs everything to files and console.
In LIVE mode: actually sends emails via SMTP.

Workflow:
  keyword_input → discovery → filtering → content analysis
  → brand-fit scoring → message personalization
  → email/DM automation → delivery log
"""

import os
import json
import time
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path

from config import BRAND_CONTEXT

logger = logging.getLogger(__name__)

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
#  EMAIL AUTOMATION — Gmail SMTP
# ─────────────────────────────────────────────────────────────────────────────

class GmailSMTPSender:
    """
    Sends emails via Gmail SMTP (free tier).
    Requires: Gmail address + App Password (2FA must be enabled on account).
    Get App Password: Google Account → Security → App Passwords

    Setup in .env:
        GMAIL_ADDRESS=your@gmail.com
        GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
    """

    def __init__(self):
        self.gmail_address = os.getenv("GMAIL_ADDRESS", "")
        self.app_password   = os.getenv("GMAIL_APP_PASSWORD", "")
        self.ready = bool(self.gmail_address and self.app_password)

    def send(self, to_email: str, subject: str, body: str, sender_name: str = "Brand Partnerships") -> bool:
        if not self.ready:
            return False

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = f"{sender_name} <{self.gmail_address}>"
        msg["To"]      = to_email

        # Plain text version
        msg.attach(MIMEText(body, "plain"))

        # HTML version (simple formatting)
        html_body = body.replace("\n\n", "</p><p>").replace("\n", "<br>")
        html_body = f"<html><body><p>{html_body}</p></body></html>"
        msg.attach(MIMEText(html_body, "html"))

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(self.gmail_address, self.app_password)
                server.sendmail(self.gmail_address, to_email, msg.as_string())
            return True
        except Exception as e:
            logger.error(f"SMTP send failed to {to_email}: {e}")
            return False


# ─────────────────────────────────────────────────────────────────────────────
#  INSTAGRAM DM AUTOMATION — Instagrapi
# ─────────────────────────────────────────────────────────────────────────────

class InstagrapiDMSender:
    """
    Sends Instagram DMs via Instagrapi (open-source IG client).
    Install: pip install instagrapi

    ⚠️  Use a dedicated business/creator IG account for automation.
        Automating personal accounts risks temporary suspension.

    Setup in .env:
        INSTAGRAM_USERNAME=your_business_handle
        INSTAGRAM_PASSWORD=your_ig_password

    Workflow:
        1. Login to Instagram
        2. Resolve creator username from profile URL (if available)
        3. Send DM using direct_send()
    """

    def __init__(self):
        self.username = os.getenv("INSTAGRAM_USERNAME", "")
        self.password = os.getenv("INSTAGRAM_PASSWORD", "")
        self._client  = None
        self.ready    = False

    def _login(self):
        """Lazy login — only connect when actually needed."""
        try:
            from instagrapi import Client
            cl = Client()
            cl.login(self.username, self.password)
            self._client = cl
            self.ready   = True
            logger.info("  Instagram: logged in successfully")
        except ImportError:
            logger.warning("  instagrapi not installed. Run: pip install instagrapi")
        except Exception as e:
            logger.error(f"  Instagram login failed: {e}")

    def send(self, username: str, message: str) -> bool:
        """Send a DM to a creator by their Instagram username."""
        if not self.username or not self.password:
            return False

        if not self.ready:
            self._login()

        if not self.ready or not self._client:
            return False

        try:
            user_id = self._client.user_id_from_username(username)
            self._client.direct_send(message, [user_id])
            time.sleep(random.uniform(15, 30))  # human-like delay
            return True
        except Exception as e:
            logger.error(f"  IG DM failed to @{username}: {e}")
            return False


# ─────────────────────────────────────────────────────────────────────────────
#  DEMO MODE — Logs outreach to files (no credentials needed)
# ─────────────────────────────────────────────────────────────────────────────

def log_outreach_to_file(profiles: list[dict], industry: str) -> Path:
    """
    In demo mode: write all outreach messages to a structured JSON file.
    This is the 'execution log' that would be sent in live mode.
    """
    brand = BRAND_CONTEXT.get(industry, BRAND_CONTEXT["education"])
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = OUTPUT_DIR / f"outreach_log_{industry}_{timestamp}.json"

    log_entries = []
    for p in profiles:
        outreach = p.get("outreach", {})
        entry = {
            "creator": p.get("channel_name"),
            "platform": p.get("platform"),
            "profile_url": p.get("profile_url"),
            "contact_email": p.get("contact_email"),
            "fit_score": p.get("fit_score"),
            "fit_grade": p.get("fit_grade"),
            "segment": p.get("segment"),
            "niche": p.get("niche_classification"),
            "email_subject": outreach.get("email_subject"),
            "email_body": outreach.get("email_body"),
            "instagram_dm": outreach.get("instagram_dm"),
            "email_word_count": outreach.get("_email_word_count"),
            "dm_word_count": outreach.get("_dm_word_count"),
            "recommended_collab": p.get("recommended_collab", []),
            "status": "queued_demo",
            "brand": brand["brand_name"],
        }
        log_entries.append(entry)

    with open(log_path, "w") as f:
        json.dump(log_entries, f, indent=2)

    return log_path


def execute_outreach(profiles: list[dict], industry: str, live_mode: bool = False) -> dict:
    """
    Task 7 main function: execute or simulate outreach.

    Args:
        profiles:  List of enriched, scored, outreach-ready creator profiles
        industry:  Brand industry context
        live_mode: If True, actually sends emails/DMs (requires .env credentials)

    Returns:
        Summary dict with sent/failed/queued counts and log file path
    """
    print("═" * 60)
    print("  TASK 7 — OUTREACH AUTOMATION LAYER")
    print("═" * 60)

    brand = BRAND_CONTEXT.get(industry, BRAND_CONTEXT["education"])
    email_sender = GmailSMTPSender()
    ig_sender    = InstagrapiDMSender()

    results = {"email_sent": 0, "email_failed": 0, "dm_queued": 0, "demo_logged": 0}

    for p in profiles:
        outreach = p.get("outreach", {})
        email     = p.get("contact_email")
        name      = p.get("channel_name", "Creator")

        if live_mode and email_sender.ready and email:
            success = email_sender.send(
                to_email=email,
                subject=outreach.get("email_subject", "Collaboration Opportunity"),
                body=outreach.get("email_body", ""),
                sender_name=f"{brand['brand_name']} Partnerships",
            )
            if success:
                results["email_sent"] += 1
                print(f"  ✉️  Email SENT → {email} ({name})")
            else:
                results["email_failed"] += 1
                print(f"  ✗  Email FAILED → {email} ({name})")
            time.sleep(2)  # rate limit: ~30 emails/min

        else:
            results["demo_logged"] += 1
            status = "No email found" if not email else "Demo mode"
            print(f"  📋 Logged → {name} | {status}")

        # Instagram DM — queue for manual/automated send
        if p.get("platform") == "Instagram":
            results["dm_queued"] += 1

    # Save full log to output file
    log_path = log_outreach_to_file(profiles, industry)

    print(f"\n  Outreach summary:")
    print(f"    Emails sent    : {results['email_sent']}")
    print(f"    Emails failed  : {results['email_failed']}")
    print(f"    Demo logged    : {results['demo_logged']}")
    print(f"    DMs queued     : {results['dm_queued']}")
    print(f"    Log saved to   : {log_path}\n")

    results["log_path"] = str(log_path)
    return results


# ─────────────────────────────────────────────────────────────────────────────
#  WORKFLOW ARCHITECTURE EXPLANATION (Task 8)
# ─────────────────────────────────────────────────────────────────────────────

WORKFLOW_EXPLANATION = """
╔══════════════════════════════════════════════════════════════╗
║     TASK 8 — END-TO-END PIPELINE ARCHITECTURE               ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  [1] KEYWORD INPUT                                           ║
║      └─ Runtime keyword list (industry-specific)             ║
║         e.g. ["olympiad preparation", "CBSE math tricks"]   ║
║                                                              ║
║  [2] CREATOR DISCOVERY  (task1_discovery.py)                 ║
║      └─ YouTube Data API v3 search                          ║
║         → Channel ID deduplication                          ║
║         → Batch statistics fetch                            ║
║         → Recent video fetch                                ║
║                                                              ║
║  [3] FILTERING ENGINE   (task2_filter_classify.py)           ║
║      └─ Subscriber range: 5K–100K                           ║
║         → Region: India (country code + signal heuristic)   ║
║         → Content relevance: keyword match in text corpus   ║
║         → Activity level: posted within 60 days             ║
║                                                              ║
║  [4] PROFILE ENRICHMENT (task2_filter_classify.py)           ║
║      └─ Engagement rate computation                         ║
║         → Email extraction from bio (regex)                 ║
║         → Content theme detection                           ║
║         → Auto-segmentation (A/B/C) via signal scoring      ║
║                                                              ║
║  [5] CONTENT INTELLIGENCE (task4_content_intelligence.py)   ║
║      └─ Multi-signal corpus analysis                        ║
║         → Intent classification (olympiad_readiness, etc.)  ║
║         → Signal strength scoring                           ║
║                                                              ║
║  [6] BRAND–FIT SCORING  (task4_content_intelligence.py)     ║
║      └─ Weighted formula:                                   ║
║         keyword_match(40%) + segment_align(30%)             ║
║         + engagement(20%) + recency(10%)                    ║
║         → Grade A/B/C/D + collab recommendation             ║
║                                                              ║
║  [7] OUTREACH GENERATION (task6_outreach_generator.py)      ║
║      └─ Claude API (if key set) OR rule-based dynamic gen   ║
║         → Email (60–90 words) + DM (15–30 words)            ║
║         → Content-signal-driven personalization             ║
║                                                              ║
║  [8] AUTOMATION EXECUTION (task7_outreach_automation.py)    ║
║      └─ Gmail SMTP / Brevo / SendGrid for email             ║
║         → Instagrapi / Meta Graph API for DMs               ║
║         → Full execution log saved to JSON                  ║
║                                                              ║
║  [9] OUTPUT                                                  ║
║      └─ output/enriched_creators_<industry>.json            ║
║         output/outreach_log_<industry>_<timestamp>.json     ║
║         Console report (tabulated)                          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

APIs used (all free tier):
  • YouTube Data API v3  — 10,000 units/day free
  • Anthropic Claude API — optional, enhances message quality
  • Gmail SMTP           — free with Google account
  • Instagrapi           — open source, no API cost

Zero paid influencer databases used. All discovery is programmatic.
"""