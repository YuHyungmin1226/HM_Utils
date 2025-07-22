# 이미지 도구 (Image Tools)

이 폴더에는 이미지 처리와 관련된 유틸리티 프로그램들이 포함되어 있습니다. 각 프로그램은 PyInstaller를 통해 실행 파일로 빌드할 수 있습니다.

## 포함된 프로그램

### ImageViewer (imgViewer.py)
- 이미지 뷰어 애플리케이션
- 지원 형식: JPG, JPEG, PNG, GIF, BMP, WEBP, TIFF, TIF
- 주요 기능:
  - 이미지 파일 열기 및 표시
  - 폴더 내 이미지 탐색 (이전/다음 이미지)
  - 전체 화면 모드 전환
  - 창 크기 조절에 따른 이미지 자동 리사이즈
  - 디버그 로그 기록
- 실행 방법:
  - Python: `python imgViewer.py`
  - 실행 파일: `./ImageViewer` 또는 `ImageViewer.app` 실행

### ImageToJPG (imgTojpg.py)
- 다양한 이미지 파일을 JPG 형식으로 변환하는 도구
- 지원 형식: PNG, JPEG, GIF, BMP, WEBP
- 주요 기능:
  - 폴더 내 모든 이미지 일괄 변환
  - 변환 진행 상황 표시
  - 변환 결과 로그 표시
- 실행 방법:
  - Python: `python imgTojpg.py`
  - 실행 파일: `./ImageToJPG` 또는 `ImageToJPG.app` 실행

### PhotoCopy (photocopy.py)
- 사진 복사 및 관리 도구
- 지원 형식: JPG, JPEG, PNG, MP4, CR3, CR2, MOV
- 주요 기능:
  - 입력/출력 폴더 선택
  - 파일 수정일 기준 폴더 생성
  - 중복 파일 체크 (SHA-256 해시)
  - 복사 진행 상황 로그 표시
  - 마지막 경로 저장 및 불러오기
- 실행 방법:
  - Python: `python photocopy.py`
  - 실행 파일: `./PhotoCopy` 또는 `PhotoCopy.app` 실행

## 빌드 방법
각 프로그램은 PyInstaller를 사용하여 실행 파일로 빌드할 수 있습니다:
```bash
# 단일 실행 파일 생성
pyinstaller --onefile --windowed --name "프로그램명" 파일명.py

# macOS 앱 번들 생성
pyinstaller --windowed --name "프로그램명" 파일명.py
```

## 시스템 요구사항
- Python 3.x
- PyInstaller
- Pillow (PIL)
- tkinter 