# 🛠️ HM_Utils - Python 유틸리티 및 도구 모음

다양한 Python 도구 및 유틸리티를 포함한 개인 프로젝트 모음입니다. 각 도구는 독립적으로 실행 가능하며, 실용적인 기능들을 제공합니다.

## 📁 프로젝트 구조

### 📝 텍스트 도구
- **`001_text_tools/`**: 텍스트 처리 도구
  - `SimpleNotepad.py` - 고급 메모장 애플리케이션 (67KB, 1413줄)

### 📊 데이터 도구
- **`002_data_tools/`**: 데이터 수집 및 분석 도구
  - `streamlit_dashboard.py` - 종합 데이터 대시보드 (멜론/벅스 차트, 도서 순위, 날씨, 뉴스)
  - `daily_info.py` - 일일 정보 수집기 (13KB, 327줄)
  - `daily_stock_recommendation.py` - 주식 추천 시스템 (6.4KB, 161줄)
  - `melon_daily_chart.py`, `bugs_daily_chart.py` - 음원 차트 수집
  - `book_rank.py` - 도서 베스트셀러 순위
  - `NewsPost.py`, `NewsAlert.py` - 뉴스 수집 및 알림
  - `Weather_review_auto.py` - 날씨 정보 자동 수집

### ⏰ 시간 도구
- **`003_time_tools/`**: 시간 관련 도구
  - `Timer.py` - 타이머 애플리케이션 (6KB, 148줄)

### 🛠️ 유틸리티
- **`004_utils/`**: 개발 및 유지보수 도구
  - `cleanup.py` - 프로젝트 폴더 정리 도구 (4.8KB, 124줄)
  - `download_nltk_data.py` - NLTK 데이터 다운로더
  - `spec_files/` - PyInstaller 스펙 파일 모음

### 🎮 게임 프로젝트
- **`005_game_projects/`**: 게임 개발 프로젝트
  - `galaga.py` - 갤러그 스타일 게임 (41KB, 1008줄)
  - `simple_tetris.py` - 테트리스 게임 (24KB, 629줄)
  - `tetris_scores.json`, `galaga.json` - 게임 점수 저장 파일

### 🎓 학교 도구
- **`006_school_tools/`**: 교육 관련 도구
  - `student_database.py` - 학생 데이터베이스 관리 시스템 (20KB, 407줄)

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
```bash
# 텍스트 도구 실행
python 001_text_tools/SimpleNotepad.py

# 데이터 대시보드 실행
streamlit run 002_data_tools/streamlit_dashboard.py

# 타이머 실행
python 003_time_tools/Timer.py

# 유틸리티 실행
python 004_utils/cleanup.py

# 게임 실행
python 005_game_projects/galaga.py
python 005_game_projects/simple_tetris.py

# 학생 데이터베이스 실행
python 006_school_tools/student_database.py
```

## 🏗️ 애플리케이션 빌드

PyInstaller를 사용하여 독립 실행형 애플리케이션을 빌드할 수 있습니다:

```bash
# Windows
pyinstaller --onefile --noconsole --name "프로그램명" 경로/프로그램명.py

# macOS
pyinstaller --onefile --windowed --name "프로그램명" 경로/프로그램명.py
```

## 🧹 프로젝트 정리

프로젝트 폴더에 임시 파일이나 캐시가 누적되면 정리 도구를 사용하세요:

```bash
python 004_utils/cleanup.py
```

**정리 대상:**
- `__pycache__` 폴더
- `.pyc` 컴파일된 파일
- `.DS_Store` 파일 (macOS)
- `build` 폴더 내 임시 파일

## 📋 시스템 요구사항

- **Python**: 3.7 이상
- **운영체제**: Windows, macOS, Linux
- **추가 라이브러리**: 각 도구별 요구사항은 해당 폴더의 README.md 참조

## 🔗 별도 레포지토리

일부 프로젝트는 별도의 전용 레포지토리로 분리되었습니다:

- 🎵 **코드 진행 생성기**: [chordgenerator](https://github.com/YuHyungmin1226/chordgenerator)
- 🖼️ **이미지 뷰어**: [imageviewer](https://github.com/YuHyungmin1226/imageviewer)
- 📺 **유튜브 다운로더**: [youtube_downloader](https://github.com/YuHyungmin1226/youtube_downloader)
- 🎤 **음성 텍스트 변환**: [speechTotext](https://github.com/YuHyungmin1226/speechTotext)

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

---

⭐ 이 프로젝트가 도움이 되었다면 스타를 눌러주세요! 