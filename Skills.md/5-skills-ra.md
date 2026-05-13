---
name: 5-skills-ra
description: >
  Use when rendering RA (Research Analyst) view. Activated when stock
  dropdown selection changes. Calculates valuation KPIs, renders quarterly
  earnings chart, peer PER comparison, and valuation table with investment
  opinion badges. Requires files 1-3 to be read first.
allowed-tools: Read
---

## 사전 조건: RA 드롭다운 필터링

RA 뷰를 렌더링하기 전에 `1-skills-data.md` Step 3의 **RA 드롭다운 제외 기준(A·B·C)**을 반드시 적용한다.

| 제외 조건 | 기준 | 처리 |
|---|---|---|
| A — ETF/인덱스 키워드 | short_name에 TIGER·KODEX·ETF 등 포함 | RA 리스트에서 완전 제외 |
| B — 실질 데이터 전무 | per_fwd·pbr·target_price 모두 null + quarterly[] 빈 배열 | RA 리스트에서 완전 제외 |
| C — 이름 깨짐 | short_name이 `ticker,영숫자,숫자` 패턴 | 제외하지 않고 표시명만 ticker 코드로 대체 |

필터링 후 남은 종목만 드롭다운에 표시하고 RA 렌더링을 수행한다.

---

## Step 1: RA KPI 카드 5개

계산 공식: `2-skills-criteria.md` "RA 지표 계산 규칙" 기준
판단 임계값 및 색상: `2-skills-criteria.md` "RA 판단 기준" 기준
데이터: `market_data.json` → `tickers[holding].fundamentals`

### KPI 그리드 상단 안내 (필수)

KPI 카드 5개 그리드 바로 위에 **안내 문구 1줄**을 표시한다. 토글 동작 모호성 제거 목적.

```
펀더멘털 지표는 최신 공시 기준 — 기간 토글은 주가 차트에만 적용
```

- 색상: `--mute` (`#8B949E`)
- 폰트: `--fs-sm` (11px)
- 위치: 종목 헤더(Step 1.5) 아래, KPI 카드 그리드 위
- 라벨 규칙 단일 출처: `3-skills-viz.md` "기간 토글 적용 범위" 표

| # | KPI | 데이터 필드 | 우선순위/대체 | null 처리 | 보조 표시 |
|---|---|---|---|---|---|
| 1 | PER (12M Fwd) | `fundamentals.per_fwd` | per_ttm 대체 | "—" | 섹터 평균 대비 % |
| 2 | PBR | `fundamentals.pbr` | — | "—" | 섹터 평균 대비 % |
| 3 | EPS (TTM) | `fundamentals.eps_ttm` | — | "—" | YoY 증감률 |
| 4 | ROE | `fundamentals.roe` | financial_index ROE 교차검증 | "—" | 전년 대비 |
| 5 | 배당수익률 | `fundamentals.dividend_yield` | — | "—" | DPS 보조 표시 |

**목표주가 괴리율은 KPI 카드에서 제거**하고 **종목 헤더**(Step 1.5)로 이동.

---

## Step 1.5: RA 종목 헤더 (드롭다운과 KPI 카드 사이)

선택된 종목의 **요약 정보를 한 줄**로 강조 표시한다.

### 표시 항목 (좌→우 순서)
| 위치 | 내용 | 형식 / 데이터 |
|---|---|---|
| 1 | 종목명 + ticker 뱃지 | "{name_role} {ticker_role}" — 폰트 18px bold |
| 2 | 투자의견 배지 | BUY/HOLD/SELL (목표주가 괴리율 기준, 색상은 `2-skills-criteria.md`) |
| 3 | 현재가 | "현재가 {current_price:,}원" |
| 4 | 목표주가 | "목표주가 {target_price:,}원" — null이면 "목표주가 미제공" |
| 5 | 괴리율 뱃지 | "괴리율 {gap:+.1f}%" — 색상: ≥+20% green / ≤-10% red / 그 외 gray |
| 6 (우측) | 빠른 종목 전환 칩 (선택) | 같은 섹터 종목 3~5개 칩, 클릭 시 해당 종목으로 전환 |

### 레이아웃
- 1행 horizontal layout, gap 12px
- 우측 빠른 전환 칩은 `margin-left: auto`로 우측 정렬
- 빠른 전환 칩 데이터: 같은 `sector_role`인 holding 중 시가총액 상위 3~5개

### null 처리
- `target_price` null → 목표주가/괴리율/배지 모두 숨김 (BUY/HOLD/SELL 대신 "N/A" 회색 배지)
- 빠른 전환 칩 → 같은 섹터 종목 부족 시(3개 미만) 칩 영역 숨김

---

## Step 2: RA 뷰 레이아웃 (2행 구조)

```
ROW 1 (2열):
  주가 추이 vs 목표주가 (라인) | 어닝 서프라이즈 히스토리 (묶음 바)

ROW 2 (3열):
  분기별 매출·영업이익 (묶음 바) | 피어 밸류에이션 비교 (테이블) | 재무 건전성 (진행바)
```

### ROW 1 - 차트 ① 주가 추이 vs 목표주가 (라인 차트)
- 데이터: `tickers[holding].history[]` + `fundamentals.target_price`
- **기간 토글 반영**: history[]를 선택 기간으로 슬라이스 (YTD=당년 1월 첫 거래일~ / 1M=21영업일 / 3M=63영업일 / 1Y=252영업일)
- 카드 제목에 선택 기간 라벨 표기 (예: "주가 추이 vs 목표주가 (3M)")
- 주가 라인: `#3A9E9E`, 두께 2px (X: date / Y: price)
- 목표주가: 수평 점선 (`#1D9E75`, borderDash [6,3])
- 52주 밴드: `fundamentals.week52_high` / `week52_low` 수평선 (`#888780` opacity 0.3)
- 우측 상단 현재가/목표가 레이블 표시
- `target_price` null → 목표주가 라인 생략 + "목표주가 미제공" 안내

### ROW 1 - 차트 ② 어닝 서프라이즈 히스토리 (묶음 바차트, **신규**)
- 데이터: `consensus_data.json → tickers[ticker].quarters[]`
- 분기마다 컨센서스(회색) + 실제(컬러) 2개 바 나란히 표시
- 표시 지표 토글 (또는 매출 우선): **매출 / 영업이익**
- 컨센서스 바: `#888780` opacity 0.4
- 실제 바: 양수 서프라이즈 → `#1D9E75` / 음수 서프라이즈 → `#E24B4A`
- 각 분기 바 위에 서프라이즈 % 뱃지 표시 (`+8.2%` / `-3.1%` 형식)
- 뱃지 색상: 양수 → `#1D9E75` / 음수 → `#E24B4A` / null → 회색
- **금융업 처리** (`is_financial: true`):
  - 매출 서프라이즈만 표시
  - 영업이익 토글 비활성화 + `op_note` 텍스트 안내 표시
- `consensus_data.json` 없거나 ticker 미존재 → 패널 전체 숨기고 그리드 1열로 fallback

### ROW 2 - 차트 ③ 분기별 매출·영업이익 (묶음 바차트)
- 데이터: `tickers[holding].quarterly[]`
- X축: quarter / Y축: 억원 단위 (/ 100000000)
- 매출 바: `#3A9E9E` / 영업이익 바: `#C8963E`
- `quarterly[]` 비어있으면 → "분기 데이터 없음" 메시지로 대체

### ROW 2 - 차트 ④ 피어 밸류에이션 비교 (테이블, 형식 변경)
- 데이터: 동일 `fundamentals.sector` holding 종목들
- 컬럼: 종목명 | PER | PBR | ROE | 배당수익률
- 분석 대상 종목 행: `#3A9E9E` 배경 강조 + ★ 마크
- 섹터 평균 행: 회색 배경 (`#161B22`) 추가 표시
- PER 저평가(< 섹터평균 × 0.8) → 셀 텍스트 `#1D9E75`
- PER 고평가(> 섹터평균 × 1.2) → 셀 텍스트 `#E24B4A`
- null 값 → "—"
- 최대 5개 종목 (분석 대상 + per_fwd 낮은 순 4개)
- 테이블 하단: 저평가/고평가 인사이트 메시지 1줄

### ROW 2 - 차트 ⑤ 재무 건전성 (진행바)
- 5개 지표를 **horizontal progress bar** 형태로 표시:
  ROE / 부채비율 / 영업이익률 / 유동비율 / 매출액증가율(YoY)
- 각 지표마다: 라벨 + 우측 값 + 진행바 (max 100% 또는 지표별 정의)
- 데이터: `financial_index.json` 매칭 (최신 연도 우선)
- 진행바 색상:
  - ROE > 15% → `#1D9E75`
  - 부채비율 > 200% → `#C8963E`, > 400% → `#E24B4A` (금융업 제외)
  - 그 외 → `#3A9E9E` 기본
- null 값 → "—" + 진행바 0%

---

### ROW 3 - 자동 생성 인사이트 3패널 (종합 의견)

ROW 2 하단에 **3열 카드 그리드**로 종합 의견을 표시한다. 규칙 기반 템플릿으로 자동 생성.

| 패널 | 색상 테마 | 데이터 소스 | 메시지 템플릿 (예시) |
|---|---|---|---|
| **밸류에이션** | green (`#1D9E75`) | per_fwd · 섹터평균 · 목표주가 괴리율 | "PER {X}x로 섹터 평균 대비 {-Y}% 저평가 구간. 목표주가 대비 괴리율 {+Z}% — {매수 신호 유효 / 중립 / 매도 신호}" |
| **실적 모멘텀** | accent (`#3A9E9E`) | 최근 분기 서프라이즈 + EPS YoY | "최근 분기 매출 서프라이즈 {±X}%. YoY EPS 성장 {±Y}%. {Q+1 전망 / 추세 평가}" |
| **리스크** | gold (`#C8963E`) 또는 red | 부채비율 · MDD 또는 유사 | "{재무 지표 기반 1줄 평가}. {추가 모니터링 권고 또는 정상 범위}" |

**규칙**:
- 각 패널은 4~5줄, 핵심 수치는 굵게(`<strong>`) 강조
- 데이터 부족 시 패널 안에 "데이터 부족"만 표시, 패널 자체는 항상 3개 유지
- 하나의 패널에서 여러 지표 충족 시 가장 임팩트 큰 1개 메시지 우선

**색상 규칙 (밸류에이션)**:
- 저평가 + BUY → green 풀 표현
- 고평가 + SELL → red 풀 표현
- 중립 → gray 톤 다운

**색상 규칙 (실적 모멘텀)**:
- 매출 서프라이즈 ≥ +5% → accent green
- 매출 서프라이즈 ≤ -5% → red
- 그 외 → accent default

**색상 규칙 (리스크)**:
- 부채비율 > 400% (비금융) → red
- 부채비율 > 200% (비금융) → gold
- 그 외 → gold default (참고 정보 톤)

---

## Step 3: 밸류에이션 테이블 + 투자의견 배지

### 투자의견 배지 (목표주가 괴리율 기준)
| 조건 | 배지 | 색상 |
|---|---|---|
| 괴리율 ≥ +20% | 📈 BUY | `#1D9E75` |
| -10% < 괴리율 < +20% | ⚪ HOLD | `#888780` |
| 괴리율 ≤ -10% | 📉 SELL | `#E24B4A` |
| target_price null | ❓ N/A | `#888780` |

### 재무지표 패널 (financial_index.json 기반)
동일 ticker 매칭 후 아래 6개 지표 카드 표시:
ROE / 순이익률 / 영업이익증가율(YoY) / 매출액증가율(YoY) / 부채비율 / 배당성향(%)
- `bsns_year` 최신 연도 우선 (2023 → 2022 → 2021 순)
- 부채비율 > 200% → gold / > 400% → red (금융업 제외)
- `idx_val` null → "—"

---

## Quality Check

- [ ] RA 드롭다운에 조건 A(ETF 키워드) 종목이 없는가?
- [ ] RA 드롭다운에 조건 B(데이터 전무) 종목이 없는가?
- [ ] 조건 C(이름 깨진) 종목의 표시명이 ticker 코드로 대체되었는가?
- [ ] 종목 드롭다운 선택 변경 시 전체 뷰가 재렌더링되는가?
- [ ] KPI 카드 ROE 값에 따라 색상이 변경되는가?
- [ ] quarterly[] 비어있을 때 "데이터 없음"으로 대체되는가?
- [ ] 피어 비교가 테이블 형식으로 표시되고 분석대상 종목이 강조되는가?
- [ ] 투자의견 배지가 괴리율 계산값 기준으로 자동 표시되는가?
- [ ] 금융업 종목의 부채비율 색상 판단이 제외되었는가?
- [ ] ROW 1에 주가 추이 vs 목표주가 라인차트가 표시되는가?
- [ ] 어닝 서프라이즈 패널에 컨센서스/실제 + 서프라이즈 % 뱃지가 표시되는가?
- [ ] 금융업 종목은 어닝 서프라이즈에서 영업이익이 비활성화되고 op_note가 표시되는가?
- [ ] consensus_data.json 없을 때 어닝 서프라이즈 패널이 숨겨지고 fallback 처리되는가?
- [ ] 재무 건전성이 진행바 형태로 5개 지표 표시되는가?
- [ ] KPI 카드 그리드 상단에 "펀더멘털 지표는 최신 공시 기준 — 기간 토글은 주가 차트에만 적용" 안내가 표시되는가?
- [ ] 분기실적·피어·재무건전성·종합인사이트 3패널 카드 제목 옆에 `(현재 기준)` 또는 `(최신 공시 기준)` 부기가 있는가?
- [ ] 주가 추이 차트 제목이 `주가 추이 vs 목표주가 ({선택기간})` 으로 토글에 따라 갱신되는가?
