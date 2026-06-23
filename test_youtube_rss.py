# -*- coding: utf-8 -*-
"""YouTube RSS 연결만 단독으로 확인하는 테스트 파일."""

from config import load_config
from youtube_rss import fetch_latest_videos


def main() -> None:
    print("[test_youtube_rss] YouTube RSS 연결 테스트를 시작합니다.")
    config = load_config()

    failed_count = 0
    for channel_id in config.youtube_channel_ids:
        print(f"\n[test_youtube_rss] 채널 확인: {channel_id}")
        videos = fetch_latest_videos(
            channel_id=channel_id,
            max_videos=config.youtube_max_videos_per_channel,
        )
        if not videos:
            failed_count += 1
            continue

        print(f"[SUCCESS] YouTube RSS에서 최신 영상 {len(videos)}개를 가져왔습니다.")
        for video in videos:
            print(f"- 제목: {video['title']}")
            print(f"  링크: {video['url']}")
            print(f"  video_id: {video['video_id']}")
            print(f"  업로드 날짜: {video['published_at']}")
            print(f"  채널명: {video['channel_name']}")

    if failed_count:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
