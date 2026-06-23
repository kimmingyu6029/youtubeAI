# -*- coding: utf-8 -*-
"""환경변수를 읽어 앱 설정 객체로 변환합니다."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


REQUIRED_ENV_VARS = (
    "NOTION_TOKEN",
    "NOTION_DATABASE_ID",
    "GEMINI_API_KEY",
    "YOUTUBE_CHANNEL_ID",
)


@dataclass(frozen=True)
class AppConfig:
    notion_token: str
    notion_database_id: str
    gemini_api_key: str
    youtube_channel_id: str
    gemini_model: str
    notion_version: str


def load_config() -> AppConfig:
    """필수 환경변수를 확인하고 AppConfig를 반환합니다."""
    load_dotenv()

    missing_vars = [name for name in REQUIRED_ENV_VARS if not os.getenv(name)]
    if missing_vars:
        for name in missing_vars:
            print(f"[ERROR] {name}이 설정되지 않았습니다.")
        print(".env 파일 또는 GitHub Secrets를 확인하세요.")
        raise SystemExit(1)

    return AppConfig(
        notion_token=os.getenv("NOTION_TOKEN", ""),
        notion_database_id=os.getenv("NOTION_DATABASE_ID", ""),
        gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
        youtube_channel_id=os.getenv("YOUTUBE_CHANNEL_ID", ""),
        gemini_model=os.getenv("GEMINI_MODEL") or "gemini-2.5-flash",
        # 데이터베이스 엔드포인트를 쓰기 위해 안정적으로 동작하는 Notion API 버전을 사용합니다.
        notion_version=os.getenv("NOTION_VERSION") or "2022-06-28",
    )


def require_env(name: str) -> str:
    """개별 테스트 파일에서 필요한 환경변수 1개만 확인합니다."""
    load_dotenv()
    value = os.getenv(name)
    if not value:
        print(f"[ERROR] {name}이 설정되지 않았습니다.")
        print(".env 파일 또는 GitHub Secrets를 확인하세요.")
        raise SystemExit(1)
    return value
