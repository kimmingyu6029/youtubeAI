# YouTube AI Notion Auto-Summary

좋아하는 유튜버가 새 영상을 올리면 YouTube RSS로 감지하고, Gemini API로 간단 요약을 만든 뒤 Notion 데이터베이스에 자동 저장하는 Python 자동화 프로젝트입니다.

GitHub Actions에서 10분마다 실행되도록 구성되어 있어 내 컴퓨터가 꺼져 있어도 동작합니다.

## 전체 동작 구조

```text
YouTube RSS
   ↓
GitHub Actions 자동 실행
   ↓
Python 프로그램 실행
   ↓
새 영상인지 video_id로 확인
   ↓
Gemini API로 간단 요약
   ↓
Notion API로 데이터베이스 저장
```

## 폴더 구조

```text
youtube-ai-notion-summary/
├── main.py
├── youtube_rss.py
├── notion_client.py
├── summarizer.py
├── config.py
├── test_youtube_rss.py
├── test_gemini.py
├── test_notion.py
├── requirements.txt
├── .env.example
├── README.md
└── .github/
    └── workflows/
        └── run.yml
```

## Notion DB 컬럼 설정 방법

Notion에서 새 데이터베이스를 만들고 아래 컬럼을 그대로 추가합니다. 이름과 타입이 코드와 정확히 같아야 합니다.

| 컬럼명 | 타입 |
| --- | --- |
| 영상 제목 | Title |
| 영상 링크 | URL |
| 업로드 날짜 | Date |
| 채널명 | Rich text |
| 요약 | Rich text |
| 핵심 정리 | Rich text |
| video_id | Rich text |
| 상태 | Select |

`상태` Select에는 `완료` 옵션을 만들어 두면 안전합니다. `test_notion.py`는 테스트 페이지를 만들 때 `테스트` 상태를 사용합니다.

## Notion Integration 연결 방법

1. [Notion Developers](https://www.notion.so/my-integrations)에 접속합니다.
2. 새 Integration을 만들고 Internal Integration Token을 복사합니다.
3. Notion 데이터베이스 페이지를 엽니다.
4. 오른쪽 위 `...` 메뉴에서 `연결` 또는 `Add connections`를 선택합니다.
5. 방금 만든 Integration을 데이터베이스에 연결합니다.
6. 데이터베이스 URL에서 ID를 복사합니다.

예시 URL:

```text
https://www.notion.so/workspace/1234567890abcdef1234567890abcdef?v=...
```

이 경우 `1234567890abcdef1234567890abcdef` 부분이 `NOTION_DATABASE_ID`입니다.

## Gemini API 키 설정 방법

1. [Google AI Studio](https://aistudio.google.com/)에 접속합니다.
2. API Key를 생성합니다.
3. 생성한 키를 `GEMINI_API_KEY` 값으로 사용합니다.

기본 모델은 `gemini-2.5-flash`입니다. 다른 모델을 쓰고 싶으면 선택 환경변수 `GEMINI_MODEL`을 설정합니다.

## Windows에서 Python 준비하기

Python 3.11 이상을 권장합니다.

설치 여부 확인:

```bash
python --version
```

Windows에서 `python` 명령이 안 되면 아래 명령도 확인합니다.

```bash
py --version
```

Python을 새로 설치할 때는 설치 첫 화면에서 `Add python.exe to PATH`를 체크한 뒤 `Install Now`를 누르세요. 이미 설치했는데 `python` 명령이 안 되면 Python 설치 프로그램을 다시 실행하고 `Modify`에서 PATH 관련 옵션을 추가하거나, Windows 검색에서 `환경 변수`를 열어 Python 설치 경로를 `Path`에 추가합니다.

`python`이 안 되어도 Windows Python Launcher가 있으면 `py` 명령으로 실행할 수 있습니다.

## 의존성 설치

프로젝트 폴더에서 아래 둘 중 하나를 실행합니다.

```bash
pip install -r requirements.txt
```

또는:

```bash
py -m pip install -r requirements.txt
```

Python 3.11을 명시하고 싶으면:

```bash
py -3.11 -m pip install -r requirements.txt
```

## .env 파일 만들기

실제 비밀키가 들어간 `.env` 파일은 Git에 올리지 않습니다. 이 저장소에는 예시 파일인 `.env.example`만 포함합니다.

PowerShell에서 복사:

```powershell
Copy-Item .env.example .env
```

명령 프롬프트에서 복사:

```bat
copy .env.example .env
```

그다음 `.env` 파일을 열어 실제 값을 입력합니다.

```env
NOTION_TOKEN=your_real_notion_token
NOTION_DATABASE_ID=your_real_notion_database_id
GEMINI_API_KEY=your_real_gemini_api_key
YOUTUBE_CHANNEL_ID=your_real_youtube_channel_id
```

여러 유튜버를 감시하려면 `YOUTUBE_CHANNEL_IDS`에 채널 ID를 쉼표로 구분해서 넣습니다.

```env
YOUTUBE_CHANNEL_IDS=UC첫번째채널ID,UC두번째채널ID,UC세번째채널ID
```

`YOUTUBE_CHANNEL_IDS`가 있으면 여러 채널을 확인하고, 없으면 기존 `YOUTUBE_CHANNEL_ID` 하나만 확인합니다.

`.env.example`에는 예시 값만 두고, 실제 키는 절대 넣지 마세요.

## VSCode 터미널에서 실행하는 방법

1. VSCode에서 이 프로젝트 폴더를 엽니다.
2. 상단 메뉴에서 `Terminal` → `New Terminal`을 클릭합니다.
3. 터미널 경로가 프로젝트 폴더인지 확인합니다.
4. 의존성을 설치합니다.

```bash
py -m pip install -r requirements.txt
```

5. `.env.example`을 `.env`로 복사하고 실제 값을 입력합니다.
6. 아래 단계별 테스트를 순서대로 실행합니다.

## 단계별 테스트

전체 `main.py`를 바로 실행하기 전에 하나씩 확인합니다.

YouTube RSS 테스트:

```bash
py test_youtube_rss.py
```

Gemini API 테스트:

```bash
py test_gemini.py
```

Notion API 테스트:

```bash
py test_notion.py
```

`python` 명령이 PATH에 등록되어 있다면 `py` 대신 `python`을 써도 됩니다.

```bash
python test_youtube_rss.py
python test_gemini.py
python test_notion.py
```

## main.py 실행 전 체크리스트

아래 순서대로 진행하세요.

1. Python 설치 확인
2. `requirements.txt` 설치
3. `.env.example`을 복사해서 `.env` 생성
4. `.env`에 Notion, Gemini, YouTube 값 입력
5. `test_youtube_rss.py` 실행
6. `test_gemini.py` 실행
7. `test_notion.py` 실행
8. 모두 성공하면 `main.py` 실행
9. 마지막으로 GitHub Secrets 등록
10. GitHub Actions에서 수동 실행 테스트

## main.py 실행 방법

아래 명령 중 현재 PC에서 되는 것을 사용합니다.

```bash
python main.py
```

또는:

```bash
py main.py
```

또는 Python 3.11을 명시:

```bash
py -3.11 main.py
```

실행하면 터미널에 RSS 조회, Notion 중복 확인, Gemini 요약, Notion 저장 로그가 출력됩니다.

## GitHub Secrets 설정 방법

GitHub 저장소에서 `Settings` → `Secrets and variables` → `Actions` → `New repository secret`으로 아래 값을 등록합니다.

```text
NOTION_TOKEN
NOTION_DATABASE_ID
GEMINI_API_KEY
YOUTUBE_CHANNEL_ID
YOUTUBE_CHANNEL_IDS
```

선택 값:

```text
GEMINI_MODEL
```

`.env` 파일은 로컬 테스트용이고, GitHub Actions에서는 GitHub Secrets 값을 사용합니다.

## GitHub Actions 수동 실행 방법

이 프로젝트에는 `.github/workflows/run.yml`이 포함되어 있습니다.

```yaml
on:
  schedule:
    - cron: "*/10 * * * *"
  workflow_dispatch:
```

수동 실행 순서:

1. GitHub 저장소에 접속합니다.
2. `Actions` 탭을 클릭합니다.
3. 왼쪽 목록에서 `YouTube AI Notion Summary` workflow를 선택합니다.
4. `Run workflow` 버튼을 클릭합니다.
5. 브랜치를 확인하고 다시 `Run workflow`를 클릭합니다.
6. 실행 중인 workflow를 눌러 로그를 확인합니다.
7. `Install dependencies` 단계에서 `pip install -r requirements.txt`가 성공했는지 확인합니다.
8. `Run program` 단계에서 오류가 없는지 확인합니다.
9. Notion DB에 새 영상 정보가 저장됐는지 확인합니다.

GitHub의 스케줄 실행은 정확히 초 단위로 보장되지 않아 몇 분 정도 지연될 수 있습니다.

## 자주 발생하는 오류와 해결법

### 환경변수가 설정되지 않았습니다

아래처럼 출력되면 `.env` 파일 또는 GitHub Secrets에 해당 값이 없습니다.

```text
[ERROR] NOTION_TOKEN이 설정되지 않았습니다.
.env 파일 또는 GitHub Secrets를 확인하세요.
```

필수 값:

```text
NOTION_TOKEN
NOTION_DATABASE_ID
GEMINI_API_KEY
YOUTUBE_CHANNEL_ID
YOUTUBE_CHANNEL_IDS
```

### Notion DB 컬럼명이 맞지 않습니다

아래처럼 출력되면 Notion DB 컬럼명이나 타입이 코드와 다를 수 있습니다.

```text
[ERROR] Notion DB 컬럼명이 코드와 일치하지 않을 수 있습니다.
README의 컬럼명과 Notion DB 속성명을 다시 확인하세요.
```

컬럼명이 `영상 제목`, `영상 링크`, `업로드 날짜`, `채널명`, `요약`, `핵심 정리`, `video_id`, `상태`와 정확히 같은지 확인하세요.

### Notion에서 404 오류가 발생합니다

대부분 아래 원인입니다.

1. `NOTION_DATABASE_ID`가 잘못됨
2. Notion 데이터베이스가 Integration과 연결되지 않음
3. Notion 토큰이 다른 워크스페이스의 Integration 토큰임

데이터베이스 오른쪽 위 `...` 메뉴에서 Integration 연결을 다시 확인하세요.

### YouTube RSS에서 영상을 가져오지 못합니다

아래처럼 출력되면 `YOUTUBE_CHANNEL_ID` 또는 `YOUTUBE_CHANNEL_IDS` 값을 확인하세요.

```text
[ERROR] YouTube RSS에서 영상을 가져오지 못했습니다.
YOUTUBE_CHANNEL_ID가 올바른지 확인하세요.
```

YouTube 핸들 주소나 커스텀 URL이 아니라 `UC...`로 시작하는 채널 ID가 필요합니다.

여러 채널을 감시할 때는 쉼표로 구분합니다.

```env
YOUTUBE_CHANNEL_IDS=UC첫번째채널ID,UC두번째채널ID
```

RSS URL 형식:

```text
https://www.youtube.com/feeds/videos.xml?channel_id=채널ID
```

### Gemini API 호출에 실패합니다

`GEMINI_API_KEY`가 맞는지, `GEMINI_MODEL` 값이 사용 가능한 모델명인지, Google AI Studio에서 API 키가 활성화되어 있는지 확인하세요.

`main.py`에서는 Gemini 요약이 실패해도 프로그램을 멈추지 않고 아래 값을 Notion에 저장합니다.

```text
요약: 요약 생성 실패
핵심 정리: Gemini API 호출 중 오류가 발생했습니다.
```

## 향후 확장 계획

v1.0 이후에는 아래 기능을 추가할 수 있습니다.

- 여러 유튜버 감시
- `channels.json`으로 채널 목록 관리
- 공개 자막 기반 요약
- 카테고리 자동 분류
- 보안 / 개발 / AI / 투자 / 자기계발 태그 자동 생성
- 영상 중요도 자동 평가
- Notion에 키워드 컬럼 추가
- 요약 실패 시 재시도 기능
