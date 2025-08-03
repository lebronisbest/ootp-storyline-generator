# ⚾ OOTP 스토리라인 생성기

🎮 **Out of the Park Baseball**의 스토리라인 XML 파일을 관리하고 편집할 수 있는 현대적인 GUI 도구입니다.

![GitHub release](https://img.shields.io/github/v/release/lebronisbest/ootp-storyline-generator?style=flat-square)
![Python](https://img.shields.io/badge/python-3.6+-blue.svg?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-green.svg?style=flat-square)

## ✨ 주요 특징

- **🎨 현대적인 UI/UX**: 더 깔끔하고 직관적인 인터페이스
- **📊 실시간 통계**: 스토리라인 개수 및 상태 정보 표시
- **🔍 향상된 검색**: 실시간 검색 및 필터링
- **📋 탭 기반 상세 보기**: 기본 정보, 기사 내용, 필수 데이터를 탭으로 구분
- **⚡ 더블클릭 편집**: 목록에서 더블클릭으로 빠른 편집
- **📱 반응형 레이아웃**: 다양한 화면 크기에 최적화
- **🎯 상태 표시**: 완성도에 따른 시각적 상태 표시 (✅ 완성, ⚠️ 미완성)

## 🚀 주요 기능

- **📂 XML 파일 로드**: OOTP 스토리라인 XML 파일을 로드하고 파싱
- **🔍 스마트 검색**: 제목, ID, 카테고리별 실시간 검색 및 필터링
- **📝 스토리라인 관리**: 추가, 편집, 삭제 기능
- **💾 XML 저장**: 편집된 스토리라인을 OOTP 호환 XML 형식으로 저장
- **📄 상세 정보 보기**: 선택된 스토리라인의 모든 정보를 탭으로 구분하여 표시
- **📊 통계 정보**: 전체 스토리라인 개수 및 현재 상태 표시

## 📥 다운로드 및 실행

### 🚀 빠른 시작 (권장)

**Windows 사용자**: [Releases](https://github.com/lebronisbest/ootp-storyline-generator/releases) 페이지에서 `OOTP_Storyline_Generator.exe`를 다운로드하여 바로 실행하세요!

> 🎯 **별도 설치 불필요**: exe 파일은 모든 필요한 라이브러리가 포함된 독립 실행 파일입니다.

### 🐍 Python으로 실행

#### 요구사항
- Python 3.6 이상
- tkinter (대부분의 Python 설치에 포함됨)

#### 설치 및 실행
```bash
# 저장소 클론
git clone https://github.com/lebronisbest/ootp-storyline-generator.git
cd ootp-storyline-generator

# Python으로 실행
python ootp_storyline_gui.py
```

#### 개발자용 설치
```bash
# 의존성 설치 (exe 빌드용)
pip install -r requirements.txt

# exe 빌드
pyinstaller OOTP_Storyline_Generator.spec
```



## 사용법

### 1. XML 파일 열기
- "XML 파일 열기" 버튼을 클릭하거나 메뉴에서 "파일 > XML 파일 열기"를 선택
- OOTP 스토리라인 XML 파일을 선택하여 로드

### 2. 스토리라인 탐색
- 왼쪽 목록에서 스토리라인을 선택하면 오른쪽에 상세 정보가 표시됩니다
- 검색창을 사용하여 특정 스토리라인을 찾을 수 있습니다
- 카테고리 필터를 사용하여 특정 유형의 스토리라인만 표시할 수 있습니다

### 3. 스토리라인 편집
- 목록에서 스토리라인을 선택하고 "선택된 스토리라인 편집" 버튼을 클릭
- 기본 정보와 기사 내용을 수정할 수 있습니다

### 4. 새 스토리라인 추가
- "새 스토리라인 추가" 버튼을 클릭하여 새로운 스토리라인을 생성

### 5. 스토리라인 삭제
- 목록에서 스토리라인을 선택하고 "선택된 스토리라인 삭제" 버튼을 클릭

### 6. XML로 저장
- "XML로 저장" 버튼을 클릭하여 현재 스토리라인들을 OOTP 호환 XML 형식으로 저장

## ⌨️ 키보드 단축키

### 📁 파일 작업
- `Ctrl+O`: XML 파일 열기
- `Ctrl+S`: XML 파일 저장
- `F5`: 목록 새로고침

### 📝 스토리라인 편집
- `Ctrl+N`: 새 스토리라인 추가
- `Enter`: 선택된 스토리라인 편집 (메인 화면)
- `Delete`: 선택된 스토리라인 삭제 (메인 화면) ⭐
- `Ctrl+Enter`: 현재 스토리라인 저장
- `Ctrl+Delete`: 현재 스토리라인 삭제 (편집 모드)
- `ESC`: 메인 화면으로 돌아가기

### 📰 기사 편집
- `Ctrl+J`: 새 기사 추가
- `Ctrl+D`: 현재 기사 삭제

### 🎯 탭 전환
- `Ctrl+1~5`: 기사 속성 탭 전환

## 📁 파일 구조

```
ootp-storyline-generator/
├── dist/
│   └── OOTP_Storyline_Generator.exe  # 실행 파일 (Windows)
├── ootp_storyline_gui.py             # 메인 GUI 애플리케이션
├── ootp_attributes.json              # OOTP 속성 데이터
├── OOTP_Storyline_Generator.spec     # PyInstaller 빌드 설정
├── requirements.txt                  # Python 의존성
├── README.md                         # 프로젝트 문서
├── .gitignore                        # Git 무시 파일
└── storylines_korean.xml             # 예시 OOTP 스토리라인 파일
```

## 스토리라인 구조

각 스토리라인은 다음과 같은 구조를 가집니다:

```xml
<STORYLINE id="스토리라인ID" random_frequency="빈도" ...>
    <REQUIRED_DATA>
        <DATA_OBJECT type="PLAYER" ... />
    </REQUIRED_DATA>
    <ARTICLES>
        <ARTICLE id="기사ID" ...>
            <SUBJECT>기사 제목</SUBJECT>
            <TEXT>기사 내용</TEXT>
            <INJURY_DESCRIPTION>부상 설명</INJURY_DESCRIPTION>
        </ARTICLE>
    </ARTICLES>
</STORYLINE>
```

## 주요 속성

- **id**: 스토리라인의 고유 식별자
- **random_frequency**: 발생 빈도 (숫자가 클수록 자주 발생)
- **league_year_min/max**: 적용 가능한 연도 범위
- **only_in_season/offseason/spring**: 특정 시기에만 발생
- **is_minor_league**: 마이너리그 전용 여부
- **storyline_happens_only_once**: 한 번만 발생하는지 여부

## 문제 해결

### XML 파일 로드 오류
- XML 파일이 올바른 형식인지 확인
- 파일 경로에 한글이나 특수문자가 없는지 확인

### GUI가 표시되지 않는 경우
- Python과 tkinter가 올바르게 설치되었는지 확인
- 터미널에서 오류 메시지를 확인

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 기여

버그 리포트나 기능 제안은 이슈를 통해 제출해주세요.

## 🔄 변경 이력

### 최신 버전
- **🎨 OOTP 게임 스타일 테마**: 어두운 배경에 야구장 색상 적용
- **🗑️ Delete 키 삭제**: 메인 화면에서 Delete 키로 스토리라인 삭제
- **⌨️ Enter 키 편집**: 메인 화면에서 Enter 키로 스토리라인 편집
- **📦 독립 실행파일**: PyInstaller로 빌드된 exe 파일 제공
- **🚀 성능 최적화**: UI 렌더링 및 응답성 개선
- **📏 레이아웃 개선**: 편집 영역이 화면을 꽉 채우도록 수정
- **🔧 코드 정리**: 불필요한 개발 파일 제거 및 구조 최적화

### 이전 버전
- **🎨 현대적인 UI/UX**: 깔끔하고 직관적인 인터페이스
- **📊 실시간 통계**: 스토리라인 개수 및 상태 정보 표시
- **🔍 향상된 검색**: 실시간 검색 및 필터링 기능
- **📋 탭 기반 편집**: 기본 정보, 기사 내용을 탭으로 구분
- **⚡ 더블클릭 편집**: 목록에서 더블클릭으로 빠른 편집
- **🎯 상태 표시**: 완성도에 따른 시각적 상태 표시
- **📱 반응형 레이아웃**: 다양한 화면 크기 지원 