# 유튜브 자막 추출 도구

이 도구는 유튜브 동영상 URL에서 자막을 추출하여 텍스트 파일로 저장하고, ChatGPT를 통해 요약할 수 있도록 도와주는 프로그램입니다.

## 주요 기능

- 유튜브 동영상 URL에서 자막 추출
- 추출한 자막을 텍스트 파일로 저장
- 저장된 자막을 ChatGPT로 요약하기 위한 기능 제공

## 설치 방법

1. 필요한 패키지 설치:

```bash
pip install -r requirements.txt
```

## 사용 방법

아래 명령어로 프로그램을 실행합니다:

```bash
python youtube_chatgpt_summarizer.py
```

또는 직접 실행:

```bash
./youtube_chatgpt_summarizer.py
```

## 작동 방식

1. 프로그램 실행 시 유튜브 URL을 입력하라는 메시지가 표시됩니다.
2. 입력한 URL에서 자막을 추출합니다.
3. 추출한 자막은 다음 두 위치에 저장됩니다:
   - 프로그램 폴더 내 `/transcripts` 디렉토리
   - 사용자 홈 디렉토리의 `~/Documents/youtube_transcripts` 폴더
4. 자막을 클립보드에 복사하고 ChatGPT 웹페이지를 엽니다.
5. 사용자는 ChatGPT 입력창에 자막을 붙여넣고 요약을 요청할 수 있습니다.

## 파일 구조

- `youtube_chatgpt_summarizer.py`: 메인 프로그램 파일
- `requirements.txt`: 필요한 패키지 목록
- `transcripts/`: 추출된 자막이 저장되는 폴더

## 필요한 패키지

- youtube-transcript-api
- pyperclip (선택 사항, 클립보드 지원 향상)

## 주의사항

- 이 프로그램은 유튜브 자막을 사용할 수 있는 동영상에서만 작동합니다.
- ChatGPT API 비용 문제로 인해 API 직접 연동 대신 웹 인터페이스를 활용합니다. 