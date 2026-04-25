"""
task1_discovery.py — Real-Time Influencer Discovery Engine
Uses YouTube Data API v3 to discover micro-influencers dynamically.
No hardcoded lists — everything is keyword-driven at runtime.
"""

import time
import logging
from typing import Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import (
    YOUTUBE_API_KEY,
    YT_MAX_RESULTS_PER_KEYWORD,
    YT_MIN_VIEW_COUNT,
    TARGET_REGION,
)

logger = logging.getLogger(__name__)


def build_youtube_client():
    """Build and return an authenticated YouTube API client."""
    if YOUTUBE_API_KEY == "YOUR_YOUTUBE_API_KEY_HERE":
        raise ValueError(
            "\n[ERROR] Please set your YOUTUBE_API_KEY in the .env file.\n"
            "Get a free key at: https://console.cloud.google.com/apis/library/youtube.googleapis.com"
        )
    return build("youtube", "v3", developerKey=YOUTUBE_API_KEY)


def search_channels_by_keyword(youtube, keyword: str, max_results: int = YT_MAX_RESULTS_PER_KEYWORD) -> list[dict]:
    """
    Search YouTube for channels matching a keyword.
    Returns a list of raw channel search results.
    """
    raw_channels = []
    try:
        # Step 1: Search for videos matching keyword — channels that post these are our targets
        search_response = youtube.search().list(
            q=keyword,
            part="snippet",
            type="video",
            regionCode=TARGET_REGION,
            relevanceLanguage="hi",
            maxResults=max_results,
            order="relevance",
            videoDuration="medium",          # 4–20 min — typical educational content length
        ).execute()

        channel_ids_seen = set()
        for item in search_response.get("items", []):
            ch_id = item["snippet"]["channelId"]
            if ch_id not in channel_ids_seen:
                channel_ids_seen.add(ch_id)
                raw_channels.append({
                    "channel_id": ch_id,
                    "channel_title": item["snippet"]["channelTitle"],
                    "video_title": item["snippet"]["title"],
                    "video_description": item["snippet"]["description"],
                    "published_at": item["snippet"]["publishedAt"],
                    "discovery_keyword": keyword,
                })

        logger.info(f"  Keyword '{keyword}' → {len(raw_channels)} unique channels found")

    except HttpError as e:
        logger.error(f"  YouTube API error for keyword '{keyword}': {e}")

    return raw_channels


def fetch_channel_statistics(youtube, channel_ids: list[str]) -> dict[str, dict]:
    """
    Batch-fetch statistics + branding for up to 50 channel IDs at once.
    Returns a dict keyed by channel_id.
    """
    stats_map = {}
    # YouTube allows max 50 IDs per request
    for i in range(0, len(channel_ids), 50):
        batch = channel_ids[i:i + 50]
        try:
            response = youtube.channels().list(
                part="statistics,snippet,brandingSettings",
                id=",".join(batch),
            ).execute()

            for item in response.get("items", []):
                cid = item["id"]
                stats = item.get("statistics", {})
                snippet = item.get("snippet", {})
                branding = item.get("brandingSettings", {}).get("channel", {})

                stats_map[cid] = {
                    "subscriber_count": int(stats.get("subscriberCount", 0)),
                    "view_count": int(stats.get("viewCount", 0)),
                    "video_count": int(stats.get("videoCount", 0)),
                    "country": snippet.get("country", ""),
                    "description": snippet.get("description", ""),
                    "custom_url": snippet.get("customUrl", ""),
                    "channel_keywords": branding.get("keywords", ""),
                    "thumbnail": snippet.get("thumbnails", {}).get("default", {}).get("url", ""),
                    "published_at": snippet.get("publishedAt", ""),
                }

        except HttpError as e:
            logger.error(f"  Channel stats fetch error: {e}")

        time.sleep(0.2)   # be polite to the API

    return stats_map


def get_recent_video_data(youtube, channel_id: str) -> Optional[dict]:
    """
    Fetch the most recent video from a channel to assess activity and content signals.
    """
    try:
        response = youtube.search().list(
            part="snippet",
            channelId=channel_id,
            order="date",
            type="video",
            maxResults=1,
        ).execute()

        items = response.get("items", [])
        if not items:
            return None

        item = items[0]
        return {
            "recent_video_title": item["snippet"]["title"],
            "recent_video_description": item["snippet"]["description"],
            "recent_video_date": item["snippet"]["publishedAt"],
            "recent_video_id": item["id"].get("videoId", ""),
        }

    except HttpError:
        return None


def discover_influencers(keywords: list[str]) -> list[dict]:
    """
    Main discovery function. Accepts a list of keywords and returns a
    deduplicated list of raw influencer profiles from YouTube.

    Args:
        keywords: List of niche-specific search keywords

    Returns:
        List of raw channel dicts (pre-filtering)
    """
    print("\n" + "═" * 60)
    print("  TASK 1 — REAL-TIME INFLUENCER DISCOVERY ENGINE")
    print("═" * 60)
    print(f"  Platform  : YouTube")
    print(f"  Region    : India ({TARGET_REGION})")
    print(f"  Keywords  : {keywords}\n")

    youtube = build_youtube_client()

    # ── Step 1: Search across all keywords ───────────────────────────────────
    all_raw = []
    seen_channel_ids = set()

    for keyword in keywords:
        print(f"  🔍 Searching: '{keyword}' ...")
        results = search_channels_by_keyword(youtube, keyword)
        for r in results:
            if r["channel_id"] not in seen_channel_ids:
                seen_channel_ids.add(r["channel_id"])
                all_raw.append(r)

    print(f"\n  → {len(all_raw)} unique channels discovered across all keywords")

    # ── Step 2: Batch-fetch channel statistics ────────────────────────────────
    print("  📊 Fetching channel statistics ...")
    channel_ids = [r["channel_id"] for r in all_raw]
    stats_map = fetch_channel_statistics(youtube, channel_ids)

    # ── Step 3: Fetch recent video for each channel ───────────────────────────
    print("  🎬 Fetching recent video data ...")
    enriched = []
    for raw in all_raw:
        cid = raw["channel_id"]
        stats = stats_map.get(cid, {})

        # Skip channels where we couldn't get stats
        if not stats:
            continue

        # Fetch recent video (rate-limited — skip if quota tight)
        recent = get_recent_video_data(youtube, cid)
        time.sleep(0.1)

        profile = {
            **raw,
            **stats,
            **(recent or {}),
            "profile_url": f"https://www.youtube.com/channel/{cid}",
            "platform": "YouTube",
        }
        enriched.append(profile)

    print(f"  ✅ {len(enriched)} channels with full data ready for filtering\n")
    return enriched