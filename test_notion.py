# -*- coding: utf-8 -*-
"""Notion API 연결과 테스트 페이지 생성을 확인하는 테스트 파일."""

from __future__ import annotations

import os
from datetime import date

from config import require_env
from notion_client import NotionAPIError, NotionClient


def main() -> None:
    print("[test_notion] Notion API 연결 테스트를 시작합니다.")
    notion = NotionClient(
        token=require_env("NOTION_TOKEN"),
        database_id=require_env("NOTION_DATABASE_ID"),
        notion_version=os.getenv("NOTION_VERSION") or "2022-06-28",
    )

    video = {
        "title": "테스트 영상",
        "url": "https://www.youtube.com/watch?v=test",
        "published_at": date.today().isoformat(),
        "channel_name": "테스트 채널",
        "video_id": "test_video_id",
    }
    summary_result = {
        "summary": "Notion 연결 테스트입니다.",
        "notes": "Notion API가 정상적으로 작동하는지 확인합니다.",
    }

    try:
        notion.validate_database_schema()
        created_page = notion.create_video_page(
            video=video,
            summary_result=summary_result,
            status="테스트",
        )
    except NotionAPIError as error:
        print("[ERROR] Notion API 연결 테스트에 실패했습니다.")
        print("NOTION_TOKEN, NOTION_DATABASE_ID, DB 컬럼명, Integration 연결을 확인하세요.")
        raise SystemExit(1) from error

    print("[SUCCESS] Notion DB에 테스트 페이지를 생성했습니다.")
    if created_page.get("url"):
        print(f"생성된 페이지: {created_page['url']}")


if __name__ == "__main__":
    main()
