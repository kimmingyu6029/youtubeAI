# -*- coding: utf-8 -*-
"""Notion API와 통신하는 클라이언트."""

from __future__ import annotations

from typing import Any

import requests


NOTION_API_BASE_URL = "https://api.notion.com/v1"
RICH_TEXT_CHUNK_SIZE = 2000
REQUIRED_DATABASE_PROPERTIES = {
    "영상 제목": "title",
    "영상 링크": "url",
    "업로드 날짜": "date",
    "채널명": "rich_text",
    "요약": "rich_text",
    "핵심 정리": "rich_text",
    "video_id": "rich_text",
    "상태": "select",
}


class NotionAPIError(Exception):
    """Notion API 호출 실패를 main.py에서 구분하기 위한 예외입니다."""


class NotionClient:
    """Notion 데이터베이스 조회와 페이지 생성을 담당합니다."""

    def __init__(self, token: str, database_id: str, notion_version: str = "2022-06-28") -> None:
        self.token = token
        self.database_id = database_id
        self.notion_version = notion_version

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Notion-Version": self.notion_version,
        }

    def get_database(self) -> dict[str, Any]:
        """Notion 데이터베이스에 접근할 수 있는지 확인합니다."""
        url = f"{NOTION_API_BASE_URL}/databases/{self.database_id}"

        try:
            print("[notion] 데이터베이스 연결을 확인합니다.")
            response = requests.get(url, headers=self._headers(), timeout=30)
            response.raise_for_status()
            print("[notion] 데이터베이스 연결 성공.")
            return response.json()

        except requests.RequestException as error:
            print(f"[notion] 데이터베이스 연결 확인 실패: {error}")
            _print_notion_error_help(error)
            raise NotionAPIError from error

    def validate_database_schema(self) -> None:
        """README에 적힌 Notion DB 컬럼명과 타입이 맞는지 확인합니다."""
        database = self.get_database()
        properties = database.get("properties", {})

        missing = [name for name in REQUIRED_DATABASE_PROPERTIES if name not in properties]
        wrong_type = [
            f"{name}(현재: {properties[name].get('type')}, 필요: {expected_type})"
            for name, expected_type in REQUIRED_DATABASE_PROPERTIES.items()
            if name in properties and properties[name].get("type") != expected_type
        ]

        if missing or wrong_type:
            print("[ERROR] Notion DB 컬럼명이 코드와 일치하지 않을 수 있습니다.")
            print("README의 컬럼명과 Notion DB 속성명을 다시 확인하세요.")
            if missing:
                print(f"[notion] 누락된 컬럼: {', '.join(missing)}")
            if wrong_type:
                print(f"[notion] 타입이 다른 컬럼: {', '.join(wrong_type)}")
            raise NotionAPIError("Notion database schema does not match README.")

        print("[notion] 데이터베이스 컬럼명과 타입 확인 성공.")

    def has_video(self, video_id: str) -> bool:
        """Notion DB에 같은 video_id가 이미 있는지 확인합니다."""
        url = f"{NOTION_API_BASE_URL}/databases/{self.database_id}/query"
        payload = {
            "filter": {
                "property": "video_id",
                "rich_text": {
                    "equals": video_id,
                },
            },
            "page_size": 1,
        }

        try:
            print(f"[notion] video_id 중복 확인: {video_id}")
            response = requests.post(url, headers=self._headers(), json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            exists = len(data.get("results", [])) > 0
            print(f"[notion] 중복 확인 결과: {'이미 있음' if exists else '새 영상'}")
            return exists

        except requests.RequestException as error:
            print(f"[notion] video_id 중복 확인 실패: {error}")
            _print_notion_error_help(error)
            raise NotionAPIError from error

    def create_video_page(
        self,
        video: dict[str, str],
        summary_result: dict[str, str],
        status: str = "완료",
    ) -> dict[str, Any]:
        """새 영상 정보를 Notion DB 페이지로 저장합니다."""
        url = f"{NOTION_API_BASE_URL}/pages"
        payload = {
            "parent": {"database_id": self.database_id},
            "properties": {
                "영상 제목": {
                    "title": _title_property(video.get("title", "제목 없음")),
                },
                "영상 링크": {
                    "url": video.get("url", ""),
                },
                "업로드 날짜": {
                    "date": {"start": video.get("published_at") or None},
                },
                "채널명": {
                    "rich_text": _rich_text_property(video.get("channel_name", "")),
                },
                "요약": {
                    "rich_text": _rich_text_property(summary_result.get("summary", "")),
                },
                "핵심 정리": {
                    "rich_text": _rich_text_property(summary_result.get("notes", "")),
                },
                "video_id": {
                    "rich_text": _rich_text_property(video.get("video_id", "")),
                },
                "상태": {
                    "select": {"name": status},
                },
            },
        }

        try:
            print("[notion] 새 페이지 저장을 시작합니다.")
            response = requests.post(url, headers=self._headers(), json=payload, timeout=30)
            response.raise_for_status()
            print("[notion] Notion DB 저장 성공.")
            return response.json()

        except requests.RequestException as error:
            print(f"[notion] Notion 저장 실패: {error}")
            _print_notion_error_help(error)
            raise NotionAPIError from error


def _title_property(text: str) -> list[dict[str, Any]]:
    """Notion Title 속성은 긴 텍스트를 2000자 안쪽으로 넣어야 안전합니다."""
    safe_text = (text or "제목 없음")[:RICH_TEXT_CHUNK_SIZE]
    return [{"type": "text", "text": {"content": safe_text}}]


def _rich_text_property(text: str) -> list[dict[str, Any]]:
    """Notion rich_text는 한 조각이 2000자를 넘지 않도록 나누어 저장합니다."""
    if not text:
        return []

    chunks = [
        text[index : index + RICH_TEXT_CHUNK_SIZE]
        for index in range(0, len(text), RICH_TEXT_CHUNK_SIZE)
    ]
    return [{"type": "text", "text": {"content": chunk}} for chunk in chunks]


def _print_notion_error_help(error: requests.RequestException) -> None:
    """Notion API 오류를 초보자가 바로 확인할 수 있는 문장으로 풀어줍니다."""
    response = getattr(error, "response", None)
    if response is None:
        print("[ERROR] Notion API에 연결하지 못했습니다.")
        print("인터넷 연결 또는 NOTION_TOKEN 값을 확인하세요.")
        return

    response_text = response.text or ""
    print(f"[notion] 응답 내용: {response_text}")

    if response.status_code == 400 and (
        "validation_error" in response_text
        or "property" in response_text
        or "select" in response_text
    ):
        print("[ERROR] Notion DB 컬럼명이 코드와 일치하지 않을 수 있습니다.")
        print("README의 컬럼명과 Notion DB 속성명을 다시 확인하세요.")
    elif response.status_code == 404:
        print("[ERROR] Notion 데이터베이스를 찾지 못했습니다.")
        print("NOTION_DATABASE_ID와 Notion Integration 연결 상태를 확인하세요.")
    elif response.status_code in (401, 403):
        print("[ERROR] Notion 인증 또는 권한 문제가 발생했습니다.")
        print("NOTION_TOKEN과 데이터베이스 연결 권한을 확인하세요.")
