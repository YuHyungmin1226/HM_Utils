# 프로젝트 협업 지침 (커서AI/ChatGPT 전용)

## 1. 기본 원칙
- 모든 답변과 코드 주석은 **한글**로 작성해 주세요.
- 함수/클래스에는 반드시 **docstring**을 달아 주세요.
- 오류 발생 시, **원인과 함께 수정 방안**을 코드와 함께 설명해 주세요.
- 코드 스타일은 **PEP8**을 따르며, 변수명은 **snake_case**로 통일합니다.
- 외부 패키지는 **requirements.txt**에 명시된 것만 사용해 주세요.
- 빌드/실행/테스트 방법은 **README.md**에 자동으로 반영해 주세요.

## 2. 코드 및 파일 구조
- 프로젝트 구조는 다음과 같이 구분합니다:
  - `001_text_tools/` : 텍스트 처리 도구
  - `002_image_tools/` : 이미지 처리 도구
  - `003_media_tools/` : 미디어 처리 도구
  - `004_data_tools/` : 데이터 처리 도구
  - `005_time_tools/` : 시간 관련 도구
  - `006_utils/` : 유틸리티 도구
  - `007_game_projects/` : 게임 프로젝트
  - `008_music_tools/` : 음악 관련 도구
- 각 도구는 독립적으로 실행 가능한 단일 파일로 구성됩니다.
- 민감 정보(키, 토큰 등)는 코드에 직접 포함하지 않고, **.env 파일** 등으로 관리합니다.

## 3. 협업 및 커뮤니케이션
- 코드 리뷰 요청 시, **변경된 부분과 이유**를 요약해 주세요.
- 질문/답변 예시:
  - "이 함수의 역할을 한 줄로 설명해줘."
  - "이 부분의 예외 처리를 강화해줘."
  - "이 코드를 리팩토링해줘."
- 추가로 궁금한 점이 있으면 언제든 질문해 주세요!

## 4. 테스트 및 검증
- 주요 기능별 **체크리스트**를 만들어 테스트합니다.
- 테스트 코드 작성 시 **unittest** 또는 **pytest**를 권장합니다.
- 실행 예시와 기대 결과를 명시해 주세요.

## 5. 환경 및 배포
- 필수/권장 패키지 및 버전은 **requirements.txt** 또는 **pyproject.toml**에 명시합니다.
- OS/파이썬 버전 등 환경 정보를 README에 기록합니다.
- 빌드/배포는 **pyinstaller**를 사용하며, 다음과 같은 옵션을 권장합니다:
  - 단일 파일 빌드: `--onefile`
  - 콘솔 창 숨기기: `--windowed` (macOS), `--noconsole` (Windows)
  - 빌드 경로 지정: `--distpath`, `--workpath`
  - 아이콘 설정: `--icon=path/to/icon.icns` (macOS), `--icon=path/to/icon.ico` (Windows)
- 빌드 명령어 예시:
  ```bash
  # macOS
  pyinstaller --onefile --windowed --name "프로그램명" --distpath .. --workpath ../build 프로그램명.py
  
  # Windows
  pyinstaller --onefile --noconsole --name "프로그램명" --distpath .. --workpath ../build 프로그램명.py
  ```
- 빌드 후 불필요한 파일 정리:
  - `build/` 디렉토리
  - `dist/` 디렉토리
  - `.spec` 파일
  - `.DS_Store` 파일
  - 임시 빌드 파일들
  - 중복된 빌드 파일들 (동일 프로그램의 다른 이름으로 빌드된 파일)

## 6. 참고 자료
- 공식 문서, 레퍼런스, 예제 링크를 README 또는 이 파일에 추가할 수 있습니다.

---

> 이 지침은 커서AI/ChatGPT와의 효과적인 협업을 위해 작성되었습니다. 
> 프로젝트 상황에 맞게 자유롭게 수정/보완해 주세요. 