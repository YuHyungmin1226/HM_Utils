# 🎵 AI 코드 진행 생성기 - Streamlit 배포 가이드

## 📖 개요

tkinter 기반의 코드 진행 생성기를 Streamlit 웹 앱으로 변환하여 누구나 브라우저에서 접근할 수 있도록 배포할 수 있습니다.

## 🌐 Streamlit 버전의 장점

### ✅ **웹 기반 접근성**
- 브라우저에서 바로 실행
- 모바일/태블릿에서도 사용 가능
- 설치 없이 링크로 공유
- 크로스 플랫폼 호환성

### ✅ **개선된 사용자 경험**
- 깔끔하고 직관적인 웹 인터페이스
- 사이드바 기반 설정 패널
- 실시간 상호작용
- 반응형 레이아웃

### ✅ **간편한 배포**
- Streamlit Cloud (무료)
- GitHub 연동 자동 배포
- 별도 서버 설정 불필요

## 🚀 로컬 실행 방법

### 1. 의존성 설치
```bash
pip install -r requirements_streamlit.txt
```

### 2. 앱 실행
```bash
streamlit run streamlit_chord_generator.py
```

### 3. 브라우저에서 확인
- 자동으로 브라우저가 열림 (보통 http://localhost:8501)
- 수동 접속: http://localhost:8501

## 🌍 온라인 배포 방법

### 방법 1: Streamlit Cloud (무료, 추천)

#### 단계 1: GitHub 레포지토리 준비
```bash
# 새 레포지토리 생성하거나 기존 레포지토리 사용
git add streamlit_chord_generator.py requirements_streamlit.txt
git commit -m "Add Streamlit chord generator"
git push origin main
```

#### 단계 2: Streamlit Cloud 배포
1. [share.streamlit.io](https://share.streamlit.io) 방문
2. GitHub 계정으로 로그인
3. "Deploy an app" 클릭
4. Repository, Branch, Main file path 설정:
   - Repository: `your-username/your-repo-name`
   - Branch: `main`
   - Main file path: `008_music_tools/streamlit_chord_generator.py`
5. "Deploy!" 클릭

#### 단계 3: 공유
- 생성된 URL (예: `https://your-app-name.streamlit.app`) 공유
- 전 세계 누구나 접속 가능!

### 방법 2: Railway.app 배포

#### 1. Railway 설정 파일 생성
```bash
# Procfile 생성
echo "web: streamlit run 008_music_tools/streamlit_chord_generator.py --server.port=\$PORT --server.address=0.0.0.0" > Procfile

# runtime.txt 생성 (선택사항)
echo "python-3.11" > runtime.txt
```

#### 2. Railway에 배포
1. [railway.app](https://railway.app) 방문
2. GitHub 레포지토리 연결
3. 자동 배포 완료

### 방법 3: Heroku 배포

#### 1. Heroku 설정 파일 생성
```bash
# Procfile 생성
echo "web: streamlit run 008_music_tools/streamlit_chord_generator.py --server.port=\$PORT --server.address=0.0.0.0" > Procfile

# setup.sh 생성
cat > setup.sh << EOF
mkdir -p ~/.streamlit/
echo "[server]
headless = true
port = \$PORT
enableCORS = false
" > ~/.streamlit/config.toml
EOF
```

#### 2. Heroku CLI로 배포
```bash
heroku create your-app-name
git push heroku main
```

## 📁 필요한 파일들

```
008_music_tools/
├── streamlit_chord_generator.py    # 메인 Streamlit 앱
├── requirements_streamlit.txt      # Python 의존성
├── STREAMLIT_DEPLOY.md            # 이 가이드 파일
└── Procfile                       # 배포용 설정 (선택사항)
```

## 🔧 주요 기능

### 🎹 **코드 진행 생성**
- 키, 조성, 박자, 마디 수 설정
- A, AABA, AB 구조 선택
- 다양한 리듬 패턴

### 🎶 **멜로디 생성**
- 자동 멜로디 생성
- 이음줄/붙임줄 설정
- 멜로디만 출력 옵션

### 💾 **파일 다운로드**
- MusicXML 형식 지원
- MuseScore, Finale, Sibelius 호환
- 타임스탬프 포함 파일명

### 📱 **반응형 UI**
- 모바일 친화적 인터페이스
- 사이드바 설정 패널
- 실시간 결과 표시

## 🎯 사용법

### 1. 기본 설정
- **키**: 드롭다운에서 17개 키 선택 (C, C#, Db, D, D#, Eb, E, F, F#, Gb, G, G#, Ab, A, A#, Bb, B)
- **조성**: major (장조) / minor (단조)
- **박자**: 4/4, 3/4, 6/8
- **마디 수**: 2-64마디

### 2. 구조 설정
- **A**: 단순 반복 구조
- **AABA**: 32마디 팝송 구조  
- **AB**: 2부 형식

### 3. 멜로디 설정
- 멜로디 추가/제거
- 이음줄/붙임줄 사용
- 멜로디만 출력 옵션

### 4. 생성 및 다운로드
- "코드 진행 생성하기" 클릭
- 결과 확인
- "MusicXML 파일 생성" 클릭
- 다운로드 링크 클릭

## 🔍 트러블슈팅

### 문제 1: music21 설치 오류
```bash
# 해결방법: 시스템별 추가 설치
# macOS
brew install fluidsynth

# Ubuntu/Debian
sudo apt-get install fluidsynth

# Windows
# music21 공식 문서 참조
```

### 문제 2: 배포 시 메모리 부족
```python
# requirements_streamlit.txt에 추가
--find-links https://download.pytorch.org/whl/cpu
torch==1.9.0+cpu
```

### 문제 3: MusicXML 다운로드 안됨
- 브라우저 팝업 차단 해제
- 다른 브라우저에서 시도
- 파일 확장자를 .xml로 변경 후 시도

## 🔄 tkinter vs Streamlit 비교

| 기능 | tkinter 버전 | Streamlit 버전 |
|------|-------------|---------------|
| **실행 방식** | 로컬 설치 필요 | 브라우저에서 실행 |
| **배포** | 설치 파일 배포 | URL 링크 공유 |
| **접근성** | 플랫폼 종속적 | 크로스 플랫폼 |
| **업데이트** | 재설치 필요 | 자동 업데이트 |
| **공유** | 파일 전송 | 링크 공유 |
| **모바일 지원** | 없음 | 완전 지원 |

## 🚀 다음 단계

### 추가 개발 아이디어
1. **사용자 계정 시스템**
   - 진행 저장/불러오기
   - 즐겨찾기 기능

2. **오디오 재생**
   - 웹 오디오 API 활용
   - 실시간 코드 재생

3. **협업 기능**
   - 코드 진행 공유
   - 댓글/평가 시스템

4. **고급 화성학**
   - 재즈 화성
   - 모달 인터체인지
   - 2차 도미넌트

## 📞 지원

문제가 발생하거나 개선 제안이 있으시면:
- GitHub Issues 생성
- 이메일 문의
- Streamlit Community 포럼 활용

---

🎵 **Happy Music Making!** 🎵 