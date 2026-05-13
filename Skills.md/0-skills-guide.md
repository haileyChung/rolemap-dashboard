---
name: 0-skills-guide
description: >
  RoleMap entry point — investment dashboard generator system. Read this file
  first, then load 1-skills-data.md through 6-skills-report.md in numerical
  order before generating any output. Use when user asks to "투자 대시보드
  만들어줘", "dashboard 생성", "investment_dashboard.html", "Skills.md 읽고
  대시보드", "PM 뷰", "RA 뷰", "포트폴리오 시각화", "ETF 분석 대시보드", or
  references files in `Skills.md/` folder paired with `데이터/` folder
  containing CSV/JSON investment data.
allowed-tools: Read, Glob
---

## 이 시스템이 하는 일

투자 데이터(CSV/JSON)를 읽고 PM(펀드매니저) / RA(리서치 애널리스트)
두 가지 뷰를 자동으로 생성하는 금융 대시보드를 만든다.
컬럼명이 달라도 역할 기반 매핑으로 동일하게 작동한다.

---

## 필수 규칙

이 폴더의 파일을 **번호 순서대로 전부 읽은 후** 대시보드를 생성한다.
파일을 건너뛰거나 순서를 바꾸지 않는다.

### AI 행동 원칙 (최우선 적용)

- **Skills.md에 명시된 규칙만 따른다.** 규칙에 없는 사항은 임의로 구현하거나 추론하지 않는다.
- Skills에 없는 표시명·로직·레이아웃이 필요한 경우 → 규칙 누락으로 처리하고 코드/ticker 그대로 표시한다.
- 외부 지식(학습 데이터, 인터넷 검색 결과 등)으로 Skills 규칙을 보완하거나 대체하지 않는다.
- 규칙이 모호할 때 "더 나아 보이는" 선택을 하지 않는다. Skills 규칙을 문자 그대로 실행한다.

| 파일 | 역할 | 로딩 |
|---|---|---|
| `0-skills-guide.md` | 전체 시스템 목적 + 실행 방법 (이 파일) | 항상 |
| `1-skills-data.md` | Fast Path 적합성 판정 + 데이터 자동 감지 + **역할 기반** 컬럼 매핑 (범용 규칙) | 항상 |
| `2-skills-criteria.md` | 투자 분석 기준 + 지표 계산 공식 + 판단 임계값 | 항상 |
| `3-skills-viz.md` | 출력 파일 명세 + 차트 유형 + 색상 + 레이아웃 | 항상 |
| `4-skills-pm.md` | PM 뷰 KPI + 차트 + 리밸런싱 신호 규칙 | 항상 |
| `5-skills-ra.md` | RA 뷰 KPI + 차트 + 투자의견 배지 규칙 | 항상 |
| `6-skills-report.md` | 렌더링 순서 + 인사이트 배너 트리거 | 항상 |
| `references/role-catalog.md` | 컬럼명 → 역할 동의어 사전 (범용) | Step 1.2에서 로드 |
| `references/current-dataset.md` | 현재 데이터셋 특화 (ETF 코드·벤치마크·이름 등) | 필요 시 로드 |
| `references/design-tokens.md` | 색상·타이포·간격·표기 규칙 단일 출처 | viz/pm/ra/report에서 인용 |
| `references/insight-templates.md` | 자동 인사이트 메시지 템플릿 (배너·패널) | 6-skills-report에서 로드 |
| `references/extending-guide.md` | 새 데이터셋·자산군·시장 확장 가이드 | 확장 작업 시에만 로드 |

---

## 실행 환경 요건

- AI 툴: Claude Code / Cursor / Claude 등 모두 호환
- Python 3.8 이상 (**`build_dashboard.py` 단일 파일 어셈블리 전용**)
- 운영체제: Windows / Mac / Linux 모두 호환
- 브라우저: Chrome 최신 버전 (결과물 확인용)
- 인터넷: Chart.js CDN 로드 필요

---

## 빌드 방식 (필수 절차)

대시보드 생성은 **반드시 2단계**로 진행한다.

### Step 0: `build_dashboard.py` 생성 (단일 파일, 어셈블리 전용)

루트 디렉토리에 `build_dashboard.py` **단 하나의 Python 파일**을 작성한다.
이 파일의 **유일한 역할**은 다음과 같다:

| 허용 (Assembly Only) | 금지 (분석은 전부 JS에서) |
|---|---|
| ✅ `데이터/` 폴더 raw 텍스트 읽기 (UTF-8) | ❌ CSV/JSON 파싱 후 변환 |
| ✅ HTML 템플릿 문자열에 raw 텍스트 치환 | ❌ KPI·수익률·MDD 등 지표 계산 |
| ✅ `</script>` 이스케이프 등 안전 처리 | ❌ 컬럼 매핑·역할 매칭 |
| ✅ `investment_dashboard.html` 저장 | ❌ 데이터 필터링·집계·정렬 |

**제약**:
- Python 파일은 **`build_dashboard.py` 하나만 허용**. 보조 모듈·헬퍼 스크립트 추가 금지
- pandas·numpy 등 데이터 라이브러리 import 금지 (표준 라이브러리 `json`, `io`, `os`만)
- 모든 분석 로직(파싱·계산·매핑·렌더링)은 100% 브라우저 JavaScript에서 실행

### Step 1: 빌드 실행

```bash
python build_dashboard.py
```

→ `investment_dashboard.html` 단일 파일 생성 (모든 데이터 인라인, fetch 없음)

---

## 폴더 구조 (변경 금지)

```
루트/
├── Skills.md/
│   ├── 0-skills-guide.md         ← 이 파일 (entry point)
│   ├── 1-skills-data.md          ← 데이터 자동 감지 + 역할 매핑 (범용)
│   ├── 2-skills-criteria.md      ← 투자 분석 기준
│   ├── 3-skills-viz.md           ← 시각화·레이아웃
│   ├── 4-skills-pm.md            ← PM 뷰 규칙
│   ├── 5-skills-ra.md            ← RA 뷰 규칙
│   ├── 6-skills-report.md        ← 인사이트·렌더링 순서
│   └── references/               ← on-demand 로드 (토큰 절약)
│       ├── role-catalog.md       ← 컬럼 동의어 사전 (범용)
│       ├── current-dataset.md    ← 현재 데이터셋 특화 정보
│       ├── design-tokens.md      ← 색상·타이포·표기 단일 출처
│       ├── insight-templates.md  ← 인사이트 메시지 템플릿
│       └── extending-guide.md    ← 새 데이터·자산군 확장 가이드
└── 데이터/
    ├── market_data.json
    ├── etf_holdings_*.csv (5개)
    ├── financial_index.json
    ├── sector_targets.json       (더미)
    └── consensus_data.json       (더미)
```

**범용성 설계**: 다른 데이터셋으로 교체할 땐 `데이터/` 폴더와 `references/current-dataset.md`만 갈아끼우면 됨. 나머지 Skills 파일은 그대로.

---

## 실행 프롬프트 (복사해서 그대로 사용)

```
Skills.md/ 폴더의 파일을 모두 읽고
데이터/ 폴더의 데이터로
build_dashboard.py를 생성한 뒤 실행해
investment_dashboard.html을 만들어줘.
```

---

## 예상 출력 결과

- **파일명**: `investment_dashboard.html` (루트 디렉토리 저장)
- **PM 뷰**: ETF 드롭다운 + 패시브/테마 뱃지 + KPI 5개(수익률/AUM/Sharpe/MDD/트래킹에러) + 인사이트 배너 + 라인차트 + 도넛차트 + 리스크 모니터링 패널 + 리밸런싱 패널 + 보유종목 테이블
- **RA 뷰**: 종목 드롭다운(검색 가능) + 종목 헤더(투자의견·괴리율·동섹터 칩) + KPI 5개(PER/PBR/EPS/ROE/배당) + 인사이트 배너 + 주가 vs 목표주가 + 어닝 서프라이즈 + 분기 실적 + 피어 테이블 + 재무 건전성 + 종합 인사이트 3패널
- **공통**: 기간 토글(YTD/1M/3M/1Y) — PM은 헤더, RA는 주가 차트 카드 내부에 분리 배치 + 다크모드(#0D1117) + 우하단 디버그 패널

---

## 자주 발생하는 문제

| 문제 | 원인 | 해결 |
|---|---|---|
| 한글 깨짐 | 인코딩 미지정 | `encoding='utf-8'` 명시 |
| 차트 빈 화면 | fetch() CORS 에러 | 데이터 인라인 삽입으로 변경 |
| ETF 데이터 없음 | 조인 키 불일치 | `yfinance_ticker` 기준 조인 |
| 수익률 계산 오류 | `idx_val` 문자열 | `parseFloat()` 변환 적용 |

---

## Quality Check

- [ ] AI가 Skills.md 외부 지식으로 임의 구현한 항목이 없는가?
- [ ] Skills.md/ 7개 파일 번호 순서대로 모두 읽었는가?
- [ ] 데이터/ 7개 파일 모두 로드되었는가?
- [ ] 출력 파일명이 `investment_dashboard.html`인가?
- [ ] PM 드롭다운 기본값이 423920.KS인가?
- [ ] RA 드롭다운 기본값이 006400.KS인가?
- [ ] `build_dashboard.py` **단일 파일**만 생성되었는가? (보조 .py 파일 금지)
- [ ] `build_dashboard.py`가 raw 텍스트 인라인만 수행하는가? (파싱·계산·매핑 금지)
- [ ] 모든 데이터 분석 로직이 HTML 내 `<script>` JS에서 실행되는가?
