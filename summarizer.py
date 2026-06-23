# -*- coding: utf-8 -*-
"""Gemini API로 영상 정보를 간단히 요약합니다."""

from __future__ import annotations

from typing import Any


PROMPT_TEMPLATE = """다음 유튜브 영상 정보를 보고 Notion에 저장할 요약본을 만들어줘.

[영상 제목]
{title}

[영상 링크]
{url}

[채널명]
{channel_name}

출력 형식:
1. 한 줄 요약
2. 핵심 내용 5개
3. 배운 점
4. 중요한 키워드
"""


FALLBACK_RESULT = {
    "summary": "요약 생성 실패",
    "notes": "Gemini API 호출 중 오류가 발생했습니다.",
}


def build_summary_prompt(video: dict[str, str]) -> str:
    """나중에 자막 기반 요약을 붙이기 쉽도록 프롬프트 생성을 함수로 분리했습니다."""
    return PROMPT_TEMPLATE.format(
        title=video.get("title", ""),
        url=video.get("url", ""),
        channel_name=video.get("channel_name", ""),
    )


def summarize_video(video: dict[str, str], api_key: str, model_name: str) -> dict[str, str]:
    """Gemini API로 요약을 생성하고, 실패하면 안전한 기본값을 반환합니다."""
    prompt = build_summary_prompt(video)

    try:
        print(f"[gemini] Gemini 요약 생성 시작. model={model_name}")
        text = generate_text(api_key=api_key, model_name=model_name, prompt=prompt)
        summary = _extract_summary_line(text)
        print("[gemini] Gemini 요약 생성 성공.")
        return {
            "summary": summary,
            "notes": text,
        }

    except Exception as error:
        print("[ERROR] Gemini API 호출에 실패했습니다.")
        print("GEMINI_API_KEY와 GEMINI_MODEL 값을 확인하세요.")
        print(f"[gemini] 상세 오류: {error}")
        return FALLBACK_RESULT.copy()


def generate_text(api_key: str, model_name: str, prompt: str) -> str:
    """Gemini API에 프롬프트를 보내고 응답 텍스트를 반환합니다."""
    text = _generate_with_current_sdk(api_key=api_key, model_name=model_name, prompt=prompt)
    if not text:
        text = _generate_with_legacy_sdk(api_key=api_key, model_name=model_name, prompt=prompt)

    text = text.strip()
    if not text:
        raise RuntimeError("Gemini 응답이 비어 있습니다.")

    return text


def _generate_with_current_sdk(api_key: str, model_name: str, prompt: str) -> str:
    """현재 Google Gen AI SDK(google-genai)를 우선 사용합니다."""
    try:
        from google import genai
    except ImportError:
        return ""

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(model=model_name, contents=prompt)
    return _response_text(response)


def _generate_with_legacy_sdk(api_key: str, model_name: str, prompt: str) -> str:
    """기존 google-generativeai 패키지만 설치된 환경도 지원합니다."""
    try:
        import google.generativeai as legacy_genai
    except ImportError as error:
        raise RuntimeError("google-genai 또는 google-generativeai 패키지가 설치되어 있지 않습니다.") from error

    legacy_genai.configure(api_key=api_key)
    model = legacy_genai.GenerativeModel(model_name)
    response = model.generate_content(prompt)
    return _response_text(response)


def _response_text(response: Any) -> str:
    """SDK별 응답 객체에서 텍스트를 최대한 안전하게 꺼냅니다."""
    text = getattr(response, "text", "")
    if isinstance(text, str):
        return text
    return ""


def _extract_summary_line(text: str) -> str:
    """Gemini 결과 중 첫 번째 의미 있는 줄을 Notion의 '요약' 컬럼에 넣습니다."""
    for line in text.splitlines():
        clean_line = line.strip()
        if clean_line:
            return clean_line[:500]

    return "요약 생성 실패"
