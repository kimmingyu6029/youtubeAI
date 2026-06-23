# -*- coding: utf-8 -*-
"""YouTube RSS 피드를 읽고 최신 영상 정보를 추출합니다."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import feedparser


RSS_URL_TEMPLATE = "https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"


def build_rss_url(channel_id: str) -> str:
    """채널 ID로 YouTube RSS URL을 만듭니다."""
    return RSS_URL_TEMPLATE.format(channel_id=channel_id.strip())


def _entry_value(entry: Any, key: str, default: str = "") -> str:
    """feedparser 엔트리에서 값이 없을 때도 안전하게 문자열을 꺼냅니다."""
    value = entry.get(key, default)
    return value if isinstance(value, str) else default


def _published_at_to_iso(entry: Any) -> str:
    """RSS 날짜를 Notion Date 속성에 넣기 좋은 ISO 문자열로 변환합니다."""
    published_parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if published_parsed:
        published_dt = datetime(*published_parsed[:6], tzinfo=timezone.utc)
        return published_dt.isoformat()

    return _entry_value(entry, "published") or _entry_value(entry, "updated")


def _extract_video_id(entry: Any) -> str:
    """YouTube RSS의 video_id를 추출합니다."""
    video_id = _entry_value(entry, "yt_videoid")
    if video_id:
        return video_id

    # 일부 feedparser 환경에서는 id가 "yt:video:VIDEO_ID" 형태로 들어옵니다.
    raw_id = _entry_value(entry, "id")
    if raw_id:
        return raw_id.rsplit(":", maxsplit=1)[-1]

    return ""


def fetch_latest_video(channel_id: str) -> dict[str, str] | None:
    """RSS에서 최신 영상 1개를 가져와 dict로 반환합니다."""
    rss_url = build_rss_url(channel_id)
    print(f"[rss] YouTube RSS 요청: {rss_url}")

    try:
        feed = feedparser.parse(rss_url)

        status = getattr(feed, "status", None)
        if status and int(status) >= 400:
            raise RuntimeError(f"RSS HTTP 상태 코드가 {status}입니다.")

        if getattr(feed, "bozo", False) and not feed.entries:
            raise RuntimeError(f"RSS 파싱 오류: {getattr(feed, 'bozo_exception', '알 수 없음')}")

        if not feed.entries:
            _print_rss_fetch_error("RSS에 영상 항목이 없습니다.")
            return None

        latest_entry = feed.entries[0]
        video_id = _extract_video_id(latest_entry)
        if not video_id:
            raise RuntimeError("최신 영상의 video_id를 찾지 못했습니다.")

        video = {
            "video_id": video_id,
            "title": _entry_value(latest_entry, "title", "제목 없음"),
            "url": _entry_value(
                latest_entry,
                "link",
                f"https://www.youtube.com/watch?v={video_id}",
            ),
            "published_at": _published_at_to_iso(latest_entry),
            "channel_name": _entry_value(latest_entry, "author")
            or _entry_value(feed.feed, "title", "채널명 없음"),
        }

        print("[rss] 최신 영상 정보를 가져왔습니다.")
        return video

    except Exception as error:
        _print_rss_fetch_error(str(error))
        return None


def _print_rss_fetch_error(detail: str = "") -> None:
    """YouTube RSS 조회 실패 원인을 사용자가 확인하기 쉽게 출력합니다."""
    print("[ERROR] YouTube RSS에서 영상을 가져오지 못했습니다.")
    print("YOUTUBE_CHANNEL_ID가 올바른지 확인하세요.")
    if detail:
        print(f"[rss] 상세 오류: {detail}")
