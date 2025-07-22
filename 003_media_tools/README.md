# 미디어 도구 (Media Tools)

이 폴더에는 오디오 및 비디오 관련 도구들이 포함되어 있습니다.

## 도구 목록

### 1. YouTube 다운로더 (youtube_downloader.py)
- YouTube 영상을 다운로드하는 도구
- 영상 또는 오디오만 다운로드 가능
- 다양한 해상도/품질 옵션 지원

### 2. 음악 플레이어 (musicplayer.py)
- 간단한 음악 재생 애플리케이션
- 재생 목록 관리 기능
- 기본적인 재생 제어 기능

### 3. 음악 파일 이름 변경 도구 (music_rename.py)
- 음악 파일의 이름을 일괄 변경하는 도구
- ID3 태그 기반 파일명 변경 지원

### 4. YouTube 자막 추출 및 요약 도구 (youtube_transcript_tool)
- YouTube 영상의 자막을 추출하고 요약하는 도구
- 다양한 언어 지원

### 5. 음성-텍스트 변환 도구 (speech_to_text.py)
- 다양한 오디오 파일(mp3, wav, m4a 등)에서 텍스트 추출
- Google Speech Recognition API 및 Whisper 모델 지원
- 텍스트 저장 및 오디오 미리 듣기 기능

## 사용 방법

### 음성-텍스트 변환기 (speech_to_text.py)

1. 필수 요구사항:
   - Python 3.6 이상
   - 필요한 패키지: `SpeechRecognition`, `pydub`, `pygame`, `openai-whisper`
   - FFmpeg 설치 필요 (오디오 처리용)

2. 설치:
   ```
   pip install -r requirements.txt
   ```

   FFmpeg 설치:
   - macOS: `brew install ffmpeg`
   - Windows: [ffmpeg.org](https://ffmpeg.org/download.html)에서 다운로드
   - Linux: `sudo apt install ffmpeg` 또는 `sudo yum install ffmpeg`

3. Whisper 설정 (macOS):
   - macOS에서 SSL 인증서 관련 오류가 발생할 경우:
     ```
     /Applications/Python\ 3.x/Install\ Certificates.command
     ```
     를 실행하여 인증서를 업데이트합니다.
   - 또는 프로그램 내에서 수동으로 Whisper 모델을 다운로드합니다.

4. 실행:
   ```
   python speech_to_text.py
   ```

5. 사용법:
   - "파일 찾기" 버튼으로 음성 파일 선택
   - 인식 엔진 선택 (Google 또는 Whisper)
     - Google: 인터넷 연결 필요, 빠른 인식
     - Whisper: 로컬에서 실행, 더 정확한 결과
   - "음성 인식 시작" 버튼으로 텍스트 변환 시작
   - 결과 텍스트는 자동으로 원본 파일과 동일한 위치에 저장됨
   - "텍스트 저장" 버튼으로 다른 위치에 추가 저장 가능

6. 문제 해결:
   - Google 엔진 오류: 인터넷 연결 확인
   - Whisper 모델 로드 오류: Whisper 모델 디렉토리 확인
   - 오디오 파일 로드 오류: FFmpeg가 제대로 설치되었는지 확인

7. 참고사항:
   - Google Speech Recognition은 인터넷 연결이 필요합니다
   - Whisper 모델은 처음 사용 시 자동으로 다운로드됩니다
   - 긴 오디오 파일의 경우 처리 시간이 오래 걸릴 수 있습니다
   - **Whisper 모델은 문서 폴더의 WhisperModels 디렉토리에 저장됩니다**

# 음성-텍스트 변환 도구

이 프로그램은 다양한 오디오 파일(MP3, WAV, M4A 등)의 음성을 텍스트로 변환하는 GUI 도구입니다.

## 주요 기능

1. 다양한 오디오 형식 지원 (MP3, WAV, M4A, AAC, FLAC, OGG)
2. 구글 Speech Recognition과 OpenAI Whisper 엔진 모두 지원
3. 오디오 파일 재생 및 제어 기능
4. 다국어 인식 지원 (한국어, 영어 등)
5. 변환된 텍스트를 파일로 저장
6. **자동 텍스트 저장 기능** - 변환 완료 후 원본 파일과 동일한 이름의 텍스트 파일로 자동 저장

## 설치 요구사항

### 필수 패키지
```
pip install SpeechRecognition pydub pygame openai-whisper
```

### FFmpeg 설치
오디오 처리를 위해 FFmpeg가 필요합니다:

- macOS: `brew install ffmpeg`
- Windows: [FFmpeg 다운로드 페이지](https://ffmpeg.org/download.html)에서 다운로드

## 사용법

1. "파일 찾기" 버튼을 클릭해 오디오 파일을 선택합니다.
2. 인식 엔진(Google 또는 Whisper)을 선택합니다.
3. 언어 옵션을 선택합니다.
4. "음성 인식 시작" 버튼을 클릭합니다.
5. 변환이 완료되면 텍스트가 화면에 표시되고 원본 파일과 동일한 위치에 자동으로 저장됩니다.
6. "텍스트 저장" 버튼을 클릭하면 다른 위치에 저장할 수도 있습니다.

## 주의사항

- Google 엔진은 인터넷 연결이 필요합니다.
- Whisper 엔진은 처음 사용 시 모델을 다운로드하므로 인터넷 연결이 필요합니다.
- 큰 모델(medium, large)은 상당한 시스템 리소스를 필요로 합니다.

## 문제 해결

### Whisper 모델 다운로드 문제
SSL 인증서 검증 실패로 모델 다운로드에 문제가 있는 경우 프로그램은 자동으로 대체 방법을 시도합니다.

### FFmpeg 문제
오디오 처리 중 오류가 발생하면 FFmpeg가 올바르게 설치되었는지 확인하세요.

## 추가 정보

- **Whisper 모델은 문서 폴더의 WhisperModels 디렉토리(~/Documents/WhisperModels)에 저장됩니다.**
- 큰 오디오 파일은 자동으로 청크로 분할되어 처리됩니다. 