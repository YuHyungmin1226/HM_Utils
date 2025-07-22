# Python 유틸리티 및 도구 모음

이 저장소는 다양한 Python 도구 및 유틸리티를 포함하고 있습니다.

## 폴더 구조

- `001_text_tools/`: 텍스트 처리 도구 (메모장, 텍스트 변환 등)
- `002_image_tools/`: 이미지 처리 도구 (이미지 뷰어, 이미지 변환 등)
- `003_media_tools/`: 미디어 처리 도구 (음성 텍스트 변환, 유튜브 다운로더 등)
- `004_data_tools/`: 데이터 처리 도구 (뉴스, 주식, 차트 데이터 수집 등)
- `005_time_tools/`: 시간 관련 도구 (타이머 등)
- `006_utils/`: 유틸리티 도구 (NLTK 데이터 다운로더, 폴더 정리 도구 등)
- `007_game_projects/`: 게임 프로젝트 (갤러그, 테트리스 등)
- `008_music_tools/`: 음악 관련 도구 (MusicXML 편집기, 코드 진행 생성기 등)
- `dist/`: 배포용 빌드 파일
- `build/`: 빌드 프로세스 파일

## 설치 및 실행

1. 필요한 패키지 설치:
   ```
   pip install -r requirements.txt
   ```

2. 원하는 도구 실행:
   ```
   python 001_text_tools/SimpleNotepad.py
   ```

## 애플리케이션 빌드

PyInstaller를 사용하여 독립 실행형 애플리케이션을 빌드할 수 있습니다:

```bash
# macOS
pyinstaller --onefile --windowed --name "프로그램명" 경로/프로그램명.py

# Windows
pyinstaller --onefile --noconsole --name "프로그램명" 경로/프로그램명.py
```

## 프로젝트 정리

프로젝트 폴더에 임시 파일이나 캐시가 누적되면 아래 명령어로 정리할 수 있습니다:

```bash
# 프로젝트 폴더 정리 (캐시 파일, 임시 파일 등 제거)
python 006_utils/cleanup.py
```

이 스크립트는 다음 항목을 정리합니다:
- `__pycache__` 폴더
- `.pyc` 컴파일된 파일
- `.DS_Store` 파일 (macOS)
- `build` 폴더 내 임시 파일 (README.md 파일은 유지)

## 필요 환경

- Python 3.7 이상
- 각 도구별 요구사항은 해당 폴더의 README.md 파일을 참조하세요. 