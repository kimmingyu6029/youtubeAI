# -*- coding: utf-8 -*-
"""YouTube RSS -> Gemini summary -> Notion 저장 실행 파일."""

from config import load_config
from notion_client import NotionAPIError, NotionClient
from summarizer import summarize_video
from youtube_rss import fetch_latest_video


def main() -> None:
    """전체 자동화 흐름을 순서대로 실행합니다."""
    print("[main] YouTube AI Notion Auto-Summary를 시작합니다.")

    config = load_config()
    notion = NotionClient(
        token=config.notion_token,
        database_id=config.notion_database_id,
        notion_version=config.notion_version,
    )

    saved_count = 0
    skipped_count = 0
    failed_count = 0

    print(f"[main] 감시 채널 수: {len(config.youtube_channel_ids)}")
    for channel_id in config.youtube_channel_ids:
        print(f"[main] 채널 확인 시작: {channel_id}")
        latest_video = fetch_latest_video(channel_id)
        if latest_video is None:
            failed_count += 1
            print("[main] 이 채널은 RSS 단계 실패로 건너뜁니다.")
            continue

        print(f"[main] 최신 영상: {latest_video['title']} ({latest_video['video_id']})")

        try:
            if notion.has_video(latest_video["video_id"]):
                skipped_count += 1
                print("[main] 이미 Notion DB에 저장된 영상입니다. 이 채널은 건너뜁니다.")
                continue
        except NotionAPIError:
            failed_count += 1
            print("[main] Notion 중복 확인에 실패했습니다. 위의 [ERROR] 메시지를 확인하세요.")
            continue

        summary_result = summarize_video(
            video=latest_video,
            api_key=config.gemini_api_key,
            model_name=config.gemini_model,
        )

        try:
            notion.create_video_page(video=latest_video, summary_result=summary_result)
        except NotionAPIError:
            failed_count += 1
            print("[main] Notion 저장에 실패했습니다. 위의 [ERROR] 메시지를 확인하세요.")
            continue

        saved_count += 1
        print("[main] 새 영상 정보를 Notion DB에 저장했습니다.")

    print(
        "[main] 실행 완료: "
        f"저장 {saved_count}개, 중복 건너뜀 {skipped_count}개, 실패 {failed_count}개"
    )


if __name__ == "__main__":
    main()
