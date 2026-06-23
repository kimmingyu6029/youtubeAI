# -*- coding: utf-8 -*-
"""YouTube RSS 연결만 단독으로 확인하는 테스트 파일."""

from config import require_env
from youtube_rss import fetch_latest_video


def main() -> None:
    print("[test_youtube_rss] YouTube RSS 연결 테스트를 시작합니다.")
    channel_id = require_env("YOUTUBE_CHANNEL_ID")

    video = fetch_latest_video(channel_id)
    if video is None:
        raise SystemExit(1)

    print("[SUCCESS] YouTube RSS에서 최신 영상 정보를 가져왔습니다.")
    print(f"제목: {video['title']}")
    print(f"링크: {video['url']}")
    print(f"video_id: {video['video_id']}")
    print(f"업로드 날짜: {video['published_at']}")
    print(f"채널명: {video['channel_name']}")


if __name__ == "__main__":
    main()
