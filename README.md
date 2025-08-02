# 🛠️ HM_Utils - 다목적 Python 유틸리티 모음

**HM_Utils**는 다양한 Python 유틸리티와 도구들을 체계적으로 정리한 프로젝트입니다. 텍스트 편집부터 게임 개발, 학교 관리 시스템까지 다양한 분야의 실용적인 도구들을 제공합니다.

## 📁 프로젝트 구조

```
HM_Utils/
├── 001_text_tools/          # 📝 텍스트 편집 도구
├── 002_time_tools/          # ⏰ 시간 관리 도구  
├── 003_utils/              # 🛠️ 개발 유틸리티
├── 004_game_projects/      # 🎮 게임 개발 프로젝트
├── 005_school_tools/       # 🎓 교육 관리 도구
├── dailyinfo/              # 📊 별도 저장소 (dailyinfo)
├── .gitignore              # Git 무시 파일
├── PROJECT_GUIDELINES.md   # 프로젝트 가이드라인
├── README.md              # 프로젝트 문서
├── requirements.txt       # Python 의존성
└── student.db            # 학생 데이터베이스
```

## 🎯 주요 기능

### 📝 텍스트 도구 (`001_text_tools/`)
- **SimpleNotepad** - 고급 메모장 애플리케이션
  - ✨ **별도 저장소로 분리됨**: [SimpleNotepad](https://github.com/YuHyungmin1226/SimpleNotepad)
  - 🎨 **다크모드/라이트모드** 자동 감지 및 전환
  - 🔍 **고급 검색 기능** (Ctrl+F, 이전/다음 찾기)
  - 💾 **자동 저장** (1분/5분/10분/30분 간격 설정)
  - 🎯 **글꼴 크기 조정** (8pt~36pt, Ctrl++/Ctrl+-)
  - 🔧 **시스템 기본 프로그램 등록** (.txt 파일 연결)
  - 🌐 **크로스 플랫폼 지원** (Windows, macOS, Linux)
  - 📱 **명령줄 통합** (`python SimpleNotepad.py file.txt`)

### ⏰ 시간 도구 (`002_time_tools/`)
- **Timer.py** (6KB, 148줄) - 소리 없는 타이머 애플리케이션
  - ⏱️ **정확한 시간 설정** (HH:MM:SS 형식)
  - 🔄 **실시간 카운트다운** 표시
  - 🚫 **소리 없는 알림** (팝업 창)
  - 🎮 **게임 중 사용 최적화** (항상 위에 표시)
  - 🖱️ **시작/중단/재설정** 기능

### 🛠️ 유틸리티 (`003_utils/`)
- **cleanup.py** (4.8KB, 124줄) - 프로젝트 정리 도구
  - 🗑️ **캐시 파일 정리** (`__pycache__`, `.pyc`, `.DS_Store`)
  - 📁 **빌드 폴더 정리** (README.md 파일 유지)
  - 📊 **정리 결과 통계** 출력
  - 🎨 **컬러 출력** 지원
- **download_nltk_data.py** - NLTK 데이터 다운로더
- **spec_files/** - PyInstaller 빌드 스펙 파일 모음

### 🎮 게임 프로젝트 (`004_game_projects/`)
- **galaga.py** (41KB, 1,008줄) - 갤러그 스타일 슈팅 게임
  - 🎯 **다양한 적 타입** (보스, 중간, 기본)
  - 🎁 **아이템 시스템** (더블샷, 실드, 폭탄, 점수)
  - 🌟 **별 배경 효과** (패럴랙스 스크롤)
  - 🎵 **사운드 효과** 지원
  - 📊 **점수 시스템** 및 최고점수 저장
  - ⚙️ **JSON 설정 파일** (난이도 조정)
- **simple_tetris.py** (24KB, 629줄) - 테트리스 게임
  - 🧩 **7가지 테트로미노** (I, O, T, S, Z, J, L)
  - 🎮 **다양한 조작** (이동, 회전, 하드드롭)
  - 📈 **점수 시스템** 및 순위표
  - 🎨 **한글 폰트** 지원
  - 💾 **JSON 점수 저장**
- **tetris_scores.json**, **galaga.json** - 게임 점수 데이터

### 🎓 학교 도구 (`005_school_tools/`)
- **student_database.py** (20KB, 407줄) - 학생 관리 시스템
  - 👥 **학생 정보 관리** (학번, 이름, 등록일)
  - 📊 **평가 기록 관리** (과목, 점수, 평가일)
  - 💾 **SQLite 데이터베이스** 사용
  - 📤 **CSV 내보내기/가져오기** 기능
  - 🖥️ **PyQt5 GUI** 인터페이스
  - 📱 **반응형 디자인** (화면 크기 자동 조정)

## 🚀 설치 및 실행

### 1. 저장소 클론
```bash
git clone https://github.com/YuHyungmin1226/HM_Utils.git
cd HM_Utils
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 개별 도구 실행

#### 📝 텍스트 도구
```bash
# SimpleNotepad는 별도 저장소로 분리되었습니다
# https://github.com/YuHyungmin1226/SimpleNotepad

# 고급 메모장 실행
python SimpleNotepad.py

# 파일과 함께 실행
python SimpleNotepad.py myfile.txt
```

#### ⏰ 시간 도구
```bash
# 타이머 실행
python 002_time_tools/Timer.py
```

#### 🛠️ 유틸리티
```bash
# 프로젝트 정리
python 003_utils/cleanup.py

# NLTK 데이터 다운로드
python 003_utils/download_nltk_data.py
```

#### 🎮 게임
```bash
# 갤러그 게임
python 004_game_projects/galaga.py

# 테트리스 게임
python 004_game_projects/simple_tetris.py
```

#### 🎓 학교 도구
```bash
# 학생 관리 시스템
python 005_school_tools/student_database.py
```

## 🏗️ 애플리케이션 빌드

PyInstaller를 사용하여 독립 실행형 애플리케이션을 빌드할 수 있습니다:

```bash
# Windows
pyinstaller --onefile --noconsole --name "프로그램명" 경로/프로그램명.py

# macOS
pyinstaller --onefile --windowed --name "프로그램명" 경로/프로그램명.py

# Linux
pyinstaller --onefile --name "프로그램명" 경로/프로그램명.py
```

## 🧹 프로젝트 정리

프로젝트 폴더에 임시 파일이나 캐시가 누적되면 정리 도구를 사용하세요:

```bash
python 003_utils/cleanup.py
```

**정리 대상:**
- `__pycache__` 폴더
- `.pyc` 컴파일된 파일
- `.DS_Store` 파일 (macOS)
- `build` 폴더 내 임시 파일

## 📋 시스템 요구사항

- **Python**: 3.7 이상
- **운영체제**: Windows, macOS, Linux
- **추가 라이브러리**: 각 도구별 요구사항은 `requirements.txt` 참조

### 주요 의존성
```txt
# 게임 개발
pygame>=2.1.0

# GUI 개발
PyQt5 (학생 관리 시스템용)

# 데이터 처리
requests>=2.28.2
beautifulsoup4>=4.11.2

# 유틸리티
nltk>=3.8.1
psutil>=5.9.0
```

## 🔗 별도 레포지토리

일부 프로젝트는 별도의 전용 레포지토리로 분리되었습니다:

- 🎵 **코드 진행 생성기**: [chordgenerator](https://github.com/YuHyungmin1226/chordgenerator)
- 📊 **일일 정보 대시보드**: [dailyinfo](https://github.com/YuHyungmin1226/dailyinfo)
- 🖼️ **이미지 뷰어**: [imageviewer](https://github.com/YuHyungmin1226/imageviewer)
- 📺 **유튜브 다운로더**: [youtube_downloader](https://github.com/YuHyungmin1226/youtube_downloader)
- 🎤 **음성 텍스트 변환**: [speechTotext](https://github.com/YuHyungmin1226/speechTotext)

## 🎮 게임 조작법

### 갤러그 (galaga.py)
- **방향키**: 이동
- **스페이스바**: 발사
- **ESC**: 게임 종료

### 테트리스 (simple_tetris.py)
- **방향키**: 이동
- **위쪽 화살표**: 회전
- **스페이스바**: 하드드롭
- **P**: 일시정지

## 📊 프로젝트 통계

**총 5개 카테고리, 9+ 개별 도구:**
- 📝 **텍스트 도구**: 0개 (SimpleNotepad는 별도 저장소로 분리)
- ⏰ **시간 도구**: 1개 (Timer)
- 🛠️ **유틸리티**: 2개 (cleanup, download_nltk_data)
- 🎮 **게임 프로젝트**: 2개 (Galaga, Tetris)
- 🎓 **학교 도구**: 1개 (Student Database)

**총 코드 라인**: 약 3,500+ 줄
**총 파일 크기**: 약 160KB+

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 👨‍💻 개발자

**YuHyungmin1226** - [GitHub](https://github.com/YuHyungmin1226)

## 🔄 최근 업데이트

- ✅ **2025-01-XX**: SimpleNotepad를 별도 저장소로 분리
- ✅ **2025-07-28**: 데이터 도구를 dailyinfo 저장소로 분리
- ✅ **2025-07-28**: 폴더 넘버링 재정리 (001-005)
- ✅ **2025-07-28**: README.md 완전 최신화
- ✅ **2025-07-28**: 프로젝트 구조 최적화

---

⭐ 이 프로젝트가 도움이 되었다면 스타를 눌러주세요! 