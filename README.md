# RoleMap 투자 대시보드

> **Skills.md 기반 바이브코딩으로 자동 생성된 금융 투자 대시보드**
> 한국 ETF + KOSPI 보유종목을 PM(펀드매니저) / RA(리서치 애널리스트) 두 가지 역할 관점에서 시각화합니다.

🔗 **데모**: <https://haileychung.github.io/rolemap-dashboard/>

---

## 핵심 컨셉

**Skills.md = 단일 출처 (Single Source of Truth)**

- 모든 분석 규칙, 시각화 기준, 인사이트 생성 로직이 `Skills.md/` 폴더의 마크다운 문서에 명세화되어 있습니다.
- `build_dashboard.py`는 Skills.md 규칙만 따르는 **조립기**입니다. 분석 로직은 일절 포함하지 않으며, 데이터 파일을 HTML 템플릿에 인라인하기만 합니다.
- 실제 분석(KPI 계산, 수익률, MDD, Sharpe, 트래킹에러 등)은 **모두 브라우저 JavaScript에서 런타임에 수행**됩니다.
- 다른 데이터셋으로 교체해도 Skills.md 규칙은 그대로 작동 — **범용성 확보**.

---

## 빌드 흐름

```
┌──────────────────┐      ┌─────────────────────┐      ┌──────────────────┐
│  Skills.md/      │      │  build_dashboard.py │      │  index.html      │
│  (분석 규칙 명세) │  →   │  (조립기 — 데이터    │  →   │  (자체 완결 SPA  │
│  + 데이터/        │      │   인라인만 수행)      │      │   ~10MB)         │
└──────────────────┘      └─────────────────────┘      └──────────────────┘
                                                                 │
                                                                 ▼
                                                          GitHub Pages 배포
```

**핵심 원칙**: 생성된 `index.html`에 버그가 있어도 **HTML을 직접 패치하지 않습니다.** 항상 Skills.md 규칙을 수정하고 재빌드합니다. (Skills.md만 고치면 다른 데이터셋·다른 환경에서도 동일하게 작동)

---

## 폴더 구조

```
rolemap-dashboard/
├── index.html              ← 배포되는 대시보드 (자체 완결, 데이터 인라인)
├── build_dashboard.py      ← 조립기 (분석 로직 없음, 인라인만)
├── Skills.md/              ← 분석 규칙 명세 (단일 출처)
│   ├── 0-skills-guide.md       전체 가이드 / 빌드 절차 / 자주 발생하는 문제
│   ├── 1-skills-data.md        데이터 매핑·조인·식별자 규칙
│   ├── 2-skills-criteria.md    분석 기준·계산 공식 (수익률·MDD·Sharpe 등)
│   ├── 3-skills-viz.md         시각화·UI 컴포넌트·기간 토글 규칙
│   ├── 4-skills-pm.md          PM 뷰 구성·렌더링 규칙
│   ├── 5-skills-ra.md          RA 뷰 구성·렌더링 규칙
│   ├── 6-skills-report.md      인사이트·배너 생성 규칙
│   └── references/
│       ├── current-dataset.md      현재 데이터셋 특화 매핑
│       ├── design-tokens.md        색상·폰트·간격 토큰
│       ├── extending-guide.md      다른 데이터셋으로 확장하는 법
│       ├── insight-templates.md    인사이트 메시지 템플릿
│       └── role-catalog.md         PM/RA 역할 카탈로그
└── 데이터/                 ← 원본 데이터 (재현 가능성)
    ├── market_data.json
    ├── financial_index.json
    ├── sector_targets.json
    ├── consensus_data.json
    └── etf_holdings_*.csv
```

---

## 대시보드 구성

### PM 뷰 (펀드매니저 관점)
- ETF 단위로 본 포트폴리오 성과·리스크 모니터링
- KPI 5개: 수익률 (기간 가변), AUM, Sharpe (1Y), MDD (전체기간), 트래킹에러 (1Y)
- 누적 수익률 vs 벤치마크 라인차트 / 구성종목 도넛 / 리스크 패널 / 보유종목 테이블
- 인사이트 배너 — 리스크 한도, 집중도, 벤치마크 대비 초과수익 자동 안내

### RA 뷰 (리서치 애널리스트 관점)
- 개별 종목 단위 펀더멘털·밸류에이션 분석
- KPI 5개: PER (12M Fwd), PBR, EPS (TTM), ROE, 배당수익률
- 주가 추이 vs 목표주가 / 어닝 서프라이즈 / 분기 실적 / 동섹터 피어 비교 / 재무 건전성
- 투자의견 자동 산출 (BUY ≥ +20% / SELL ≤ -10% / HOLD)

### 공통
- 기간 토글 (YTD / 1M / 3M / 1Y) — **뷰별 분리 배치**
  - PM: 헤더 우측 (영향 항목 다수)
  - RA: 주가 차트 카드 내부 (영향 항목이 주가 차트 하나뿐 → 다른 카드 재애니메이션 방지)
- 다크 모드 (#0D1117) / 우하단 디버그 패널

---

## 로컬에서 재빌드하는 법

```bash
python build_dashboard.py
# → investment_dashboard.html 생성
```

### 데이터를 교체할 때

`데이터/` 폴더의 파일을 교체할 때 두 가지 경우로 나뉩니다:

**① 동일 스키마 (파일명·필드 구조 그대로) → python만 다시 돌리면 끝**
- `build_dashboard.py`는 데이터를 파싱하지 않고 raw 텍스트로 HTML에 인라인만 합니다
- 실제 분석은 HTML 안의 JavaScript가 런타임에 수행
- 같은 형식의 새 데이터면 `python build_dashboard.py` 한 번이면 새 대시보드 완성

**② 다른 스키마 (필드명·구조가 다름) → Skills.md 갱신 → 빌드 스크립트의 JS 갱신**
1. `Skills.md/references/current-dataset.md` 에 새 데이터셋 매핑 정의
2. `Skills.md/1-skills-data.md` 의 조인·식별자 규칙 확인·수정
3. `build_dashboard.py` 내 HTML 템플릿의 JS 데이터 접근 코드를 갱신
4. 재빌드

확장 절차는 `Skills.md/references/extending-guide.md` 에 상세히 명세되어 있습니다.

---

## 평가 항목 매핑

| 항목 | 어디서 확인 |
|---|---|
| **범용성** (25) | `Skills.md/references/extending-guide.md` — 다른 데이터셋 확장 절차 |
| **Skills.md 설계** (25) | `Skills.md/` 전체 — 7개 핵심 md + 5개 reference md |
| **대시보드 자동 생성** (25) | 데모 URL — 자동 분석 동작 / 시각화 / 인사이트 자동 생성 |
| **바이브코딩 활용** (15) | `build_dashboard.py` — 분석 로직 없는 조립기 / 모든 규칙은 Skills.md에서 |
| **실용성·창의성** (10) | PM·RA 이중 역할 뷰 / 자동 인사이트 / 기간 토글 뷰별 분리 등 |
