
# 🚀 Real-Time Automated Micro-Influencer Discovery & Contextual Outreach System

> A fully automated, keyword-driven influencer intelligence pipeline for Indian micro-influencers.
> Covers all 9 assignment tasks end-to-end with **zero paid APIs** and **no hardcoded influencer lists**.

---

## 📌 What This System Does

| Task | Description |
|------|-------------|
| **Task 1** | Real-time YouTube creator discovery via keyword search |
| **Task 2** | Automated filtering (5K–100K subs, India, active, relevant) + A/B/C segmentation |
| **Task 3** | Profile enrichment (engagement rate, email extraction, niche classification) |
| **Task 4** | Content context intelligence — detects intents from titles, descriptions, hashtags |
| **Task 5** | Brand–creator fit scoring with weighted formula + grade (A/B/C/D) |
| **Task 6** | Personalized email (60–90 words) + Instagram DM (15–30 words) generation |
| **Task 7** | Outreach automation via Gmail SMTP + Instagrapi |
| **Task 8** | End-to-end pipeline architecture diagram |
| **Task 9** | Collaboration strategy recommendation per segment |

---

## 🗂️ File Structure

```
influencer_system/
├── main.py                       # ▶ Orchestrator — run this to start the pipeline
├── config.py                     # All configuration, brand context, weights
├── task1_discovery.py            # YouTube Data API v3 discovery engine
├── task2_filter_classify.py      # Filtering + auto-segmentation + profile enrichment
├── task4_content_intelligence.py # Content signal analysis + brand-fit scoring
├── task6_outreach_generator.py   # Personalized email + DM generator
├── task7_outreach_automation.py  # Email/DM automation + pipeline architecture
├── task9_collab_strategy.py      # Collab strategy + JSON export + console report
├── requirements.txt              # Python dependencies
├── .env.example                  # Copy this to .env and add your API keys
└── output/                       # Auto-created — all JSON results saved here
```

---

## ⚡ Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd influencer_system
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up your API key
Create a `.env` file in the `influencer_system/` folder:
```
YOUTUBE_API_KEY=YOUR_KEY_HERE
```
> See [How to get a free YouTube API Key](#-how-to-get-a-free-youtube-api-key) below.

### 4. Run in Demo Mode (no API key needed)
```bash
python main.py --demo --industry education
```

### 5. Run with Live YouTube Discovery
```bash
python main.py --industry education
```

---

## 🔑 How to Get a Free YouTube API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"New Project"** → name it anything → **Create**
3. Go to **APIs & Services → Library**
4. Search **"YouTube Data API v3"** → Click **Enable**
5. Go to **APIs & Services → Credentials**
6. Click **"+ Create Credentials" → API Key**
7. Copy the key and paste it in your `.env` file:
   ```
   YOUTUBE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXX
   ```

> ✅ **Free quota:** 10,000 units/day — enough for ~80+ keyword searches daily. No credit card required.

---

## 🧪 Run Commands

```bash
# Demo mode — no API key needed, uses realistic mock data
python main.py --demo --industry education

# Live mode — real YouTube search
python main.py --industry education
python main.py --industry beauty
python main.py --industry fintech

# Custom keywords
python main.py --industry education --keywords "olympiad preparation" "CBSE math tricks" "NTSE 2024"

# Interactive mode — prompts you for industry and keywords
python main.py
```

---

## 🏗️ System Architecture

```
keyword input (runtime)
        │
        ▼
┌─────────────────────────────────────┐
│  TASK 1: Discovery Engine           │  ← YouTube Data API v3
│  • Keyword search across YouTube    │
│  • Batch channel statistics fetch   │
│  • Recent video fetch               │
│  • Channel deduplication            │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│  TASK 2: Filtering + Segmentation   │
│  • Subscribers: 5,000 – 100,000     │
│  • Region: India (code + heuristic) │
│  • Content relevance: keyword match │
│  • Activity: posted within 60 days  │
│  • Auto-segment: A / B / C          │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│  TASK 3: Profile Enrichment         │
│  • Engagement rate computation      │
│  • Email extraction from bio        │
│  • Content theme detection          │
│  • Niche classification             │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│  TASK 4: Content Intelligence       │
│  • Analyzes titles, descriptions,   │
│    hashtags, captions, keywords     │
│  • Detects intents (NOT bio-based)  │
│  • Signal strength scoring          │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│  TASK 5: Brand–Fit Scoring          │
│  • keyword_match    ×  0.40         │
│  • segment_align    ×  0.30         │
│  • engagement_rate  ×  0.20         │
│  • recency          ×  0.10         │
│  → Grade A / B / C / D              │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│  TASK 6: Outreach Generator         │  ← Claude API (optional) or rule-based
│  • Email pitch: 60–90 words         │
│  • Instagram DM: 15–30 words        │
│  • Personalized using content data  │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│  TASK 7: Automation Layer           │
│  • Gmail SMTP — email sending       │
│  • Instagrapi — Instagram DMs       │
│  • Full JSON execution log          │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│  TASK 9: Collaboration Strategy     │
│  • Maps each segment → strategy     │
│  • Paid / Affiliate / Barter /      │
│    UGC / Ambassador / Product Trial │
└──────────────────┬──────────────────┘
                   │
                   ▼
            output/ directory
   enriched_creators_<industry>.json
   outreach_log_<industry>_<ts>.json
```

---

## 📊 Creator Segments

### Education Industry
| Segment | Label | Detected Keywords |
|---------|-------|-------------------|
| A | Olympiad & Competitive Prep | olympiad, IMO, NTSE, NSO, SOF, silverzone |
| B | Reasoning & Aptitude | reasoning, aptitude, logical, IQ, mental math |
| C | Curriculum & Board Prep | CBSE, ICSE, board exam, class 10, class 12, NCERT |

### Beauty Industry
| Segment | Label | Detected Keywords |
|---------|-------|-------------------|
| A | Skincare Educators | skincare, dermatologist, serum, moisturiser |
| B | Makeup Tutorial Creators | makeup, tutorial, eyeshadow, foundation |
| C | Product Reviewers | review, unboxing, affordable, haul |

### Fintech Industry
| Segment | Label | Detected Keywords |
|---------|-------|-------------------|
| A | Investment Educators | SIP, mutual fund, stock market, investing |
| B | Budgeting Advisors | budget, savings, personal finance |
| C | Credit & Cards | credit card, CIBIL, credit score, EMI |

---

## 🤝 Collaboration Strategy Map

| Segment | Primary Strategy | Additional Options |
|---------|-----------------|-------------------|
| **A** (Education) | Paid Sponsorship | Assessment Ecosystem Partnership, Ambassador Program |
| **B** (Education) | UGC Partnerships | Barter Collaboration, Affiliate Program |
| **C** (Education) | Product Trials | Barter Collaboration, Affiliate Program |

---

## 📐 Brand–Fit Score Formula

```
fit_score = (keyword_match  × 0.40)
          + (segment_align  × 0.30)
          + (engagement_rate × 0.20)
          + (recency         × 0.10)

Grade A  →  score ≥ 0.80
Grade B  →  score ≥ 0.65
Grade C  →  score ≥ 0.50
Grade D  →  score  < 0.50   (excluded from outreach)
```

---

## 📁 Sample Output JSON

```json
{
  "platform": "YouTube",
  "channel_name": "OlympiadGuru",
  "profile_url": "https://www.youtube.com/channel/UCxxx",
  "subscriber_count": 42000,
  "engagement_rate_pct": 3.2,
  "content_themes": ["Olympiad Preparation", "Math & Reasoning"],
  "niche_classification": "Olympiad & Competitive Prep",
  "segment": "A",
  "contact_email": "olympiadguru@gmail.com",
  "detected_intents": ["olympiad_readiness", "concept_teaching"],
  "primary_intent": "olympiad_readiness",
  "fit_score": 0.74,
  "fit_grade": "B",
  "component_scores": {
    "keyword_match": 0.80,
    "segment_align": 1.00,
    "engagement_rate": 0.60,
    "recency": 1.00
  },
  "primary_collab_strategy": "Paid Sponsorship",
  "outreach": {
    "email_subject": "Collaboration opportunity for OlympiadGuru × SPARK Olympiads",
    "email_body": "Hi OlympiadGuru,\n\nYour recent video on 'IMO 2024 Preparation Strategy' stood out — the way you break down olympiad readiness for your students is exceptional.\n\nOur platform helps students prepare for olympiads with AI-adaptive practice tests — a natural fit for your audience of serious learners. We'd love to partner with you for a paid sponsorship that genuinely adds value.\n\nWould you be open to a quick 15-minute call this week?\n\nBest,\nSPARK Olympiads Partnerships Team",
    "email_word_count": 76,
    "instagram_dm": "Hey OlympiadGuru! Loved your IMO prep content 🙌 We'd love to collaborate on a paid sponsorship — DM back if interested!",
    "dm_word_count": 22
  }
}
```

---

## 📧 Live Email Setup (Gmail SMTP)

1. Enable **2-Factor Authentication** on your Google account
2. Go to **Google Account → Security → App Passwords**
3. Create a new App Password for "Mail"
4. Add to your `.env` file:
   ```
   GMAIL_ADDRESS=your@gmail.com
   GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
   ```
5. The system will automatically send emails when credentials are present

---

## 🤖 Optional: Claude AI for Better Outreach Messages

Add your Anthropic API key to `.env` to upgrade outreach generation from rule-based to AI-powered:
```
ANTHROPIC_API_KEY=sk-ant-XXXXXXXXXX
```
Get a free key at [console.anthropic.com](https://console.anthropic.com)

Without it, the built-in dynamic rule-based generator still produces personalized, content-signal-driven messages.

---

## ✅ Technical Constraints Compliance

| Constraint | Status |
|-----------|--------|
| Real-time operation | ✅ Live YouTube Data API v3 |
| No hardcoded influencer lists | ✅ 100% keyword-driven discovery |
| No paid influencer databases | ✅ Free APIs only |
| Zero-cost tools | ✅ YouTube free tier + Gmail SMTP |
| Keyword-driven discovery | ✅ Runtime keyword input supported |
| Dynamic personalization | ✅ Content-signal-based message generation |
| Category-agnostic | ✅ Education / Beauty / Fintech supported |
| Automated segmentation | ✅ Signal-scoring (not manual) |
| Automated enrichment | ✅ No manual data entry |

---

## 🛠️ APIs & Tools Used

| Tool | Purpose | Cost |
|------|---------|------|
| YouTube Data API v3 | Creator discovery & stats | Free (10K units/day) |
| Gmail SMTP | Email outreach automation | Free |
| Instagrapi | Instagram DM automation | Free (open source) |
| Anthropic Claude API | AI outreach message generation | Optional |

---

## 📜 License

MIT License — free to use, modify, and distribute.
