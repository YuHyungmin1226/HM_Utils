# PyInstaller Spec 파일

이 폴더에는 PyInstaller 빌드에 사용되는 .spec 파일들이 저장됩니다.

## 포함된 파일
- `speech_to_text.spec`: 음성 텍스트 변환기 빌드 스펙 파일
- `youtube_chatgpt_summarizer.spec`: 유튜브 자막 추출 및 ChatGPT 요약 도구 빌드 스펙 파일

## 사용 방법
빌드 시 .spec 파일을 직접 사용할 수 있습니다:
```bash
pyinstaller 006_utils/spec_files/speech_to_text.spec
pyinstaller 006_utils/spec_files/youtube_chatgpt_summarizer.spec
``` 