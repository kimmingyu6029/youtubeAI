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
    latest_video = fetch_latest_video(config.youtube_channel_id)
    if latest_video is None:
        print("[main] RSS 단계 실패로 종료합니다.")
        return

    print(f"[main] 최신 영상: {latest_video['title']} ({latest_video['video_id']})")

    notion = NotionClient(
        token=config.notion_token,
        database_id=config.notion_database_id,
        notion_version=config.notion_version,
    )

    try:
        if notion.has_video(latest_video["video_id"]):
            print("[main] 이미 Notion DB에 저장된 영상입니다. 새 작업 없이 종료합니다.")
            return
    except NotionAPIError:
        print("[main] Notion 중복 확인에 실패했습니다. 위의 [ERROR] 메시지를 확인하세요.")
        return

    summary_result = summarize_video(
        video=latest_video,
        api_key=config.gemini_api_key,
        model_name=config.gemini_model,
    )

    try:
        notion.create_video_page(video=latest_video, summary_result=summary_result)
    except NotionAPIError:
        print("[main] Notion 저장에 실패했습니다. 위의 [ERROR] 메시지를 확인하세요.")
        return

    print("[main] 새 영상 정보를 Notion DB에 저장했습니다.")


if __name__ == "__main__":
    main()
