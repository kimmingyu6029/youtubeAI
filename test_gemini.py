# -*- coding: utf-8 -*-
"""Gemini API 연결만 단독으로 확인하는 테스트 파일."""

from __future__ import annotations

import os

from config import require_env
from summarizer import generate_text


TEST_PROMPT = "Gemini API 연결 테스트입니다. 한국어로 한 문장만 짧게 답해주세요."


def main() -> None:
    print("[test_gemini] Gemini API 연결 테스트를 시작합니다.")
    api_key = require_env("GEMINI_API_KEY")
    model_name = os.getenv("GEMINI_MODEL") or "gemini-2.5-flash"

    try:
        response_text = generate_text(api_key=api_key, model_name=model_name, prompt=TEST_PROMPT)
    except Exception as error:
        print("[ERROR] Gemini API 연결 테스트에 실패했습니다.")
        print("GEMINI_API_KEY가 올바른지 확인하세요.")
        print(f"[test_gemini] 상세 오류: {error}")
        raise SystemExit(1) from error

    print("[SUCCESS] Gemini API 응답을 받았습니다.")
    print(response_text)


if __name__ == "__main__":
    main()
