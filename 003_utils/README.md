# 유틸리티 도구 (Utility Tools)

이 폴더에는 다양한 유틸리티 및 지원 프로그램이 포함되어 있습니다.

## 포함된 프로그램

### download_nltk_data.py
- NLTK(자연어 처리 툴킷) 데이터 다운로드 유틸리티
- 자연어 처리 관련 프로젝트에 필요한 데이터 패키지 설치
- 실행 방법: `python download_nltk_data.py`

### cleanup.py
- 프로젝트 폴더 정리 유틸리티
- 캐시 파일 및 임시 파일 삭제 (__pycache__, .pyc, .DS_Store)
- build 디렉토리 정리 (README.md 파일 유지)
- 실행 방법: `python 006_utils/cleanup.py`

## spec_files 디렉토리
- PyInstaller 빌드에 사용되는 .spec 파일 모음
- 자세한 내용은 `spec_files/README.md` 참조 