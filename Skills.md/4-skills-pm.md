---
name: 4-skills-pm
description: >
  Use when rendering PM (Fund Manager) view. Activated when ETF dropdown
  selection changes. Calculates portfolio KPIs, renders cumulative return
  vs benchmark chart, sector allocation donut, rebalancing signal panel,
  and holdings table. Requires files 1-3 to be read first.
allowed-tools: Read
---

## Step 0: ETF 유형 감지 (패시브 vs 테마형)

ETF 드롭다운 선택 즉시 `1-skills-data.md` "ETF 유형 분류" 기준으로 유형을 판별한다.
판별 결과는 **Step 3 하단 패널 선택**에만 영향을 미친다. KPI·차트는 유형과 무관하게 동일하게 렌더링한다.

---

## Step 1: PM KPI 카드 5개

계산 공식: `2-skills-criteria.md` "PM 지표 계산 규칙" 기준
판단 임계값 및 색상: `2-skills-criteria.md` "PM 판단 기준" 기준
데이터: `market_data.json` → `tickers[etf].returns` + `history[]` + `benchmarks[].history`

| # | KPI | 데이터 필드 | 기간 | KPI 카드 라벨 (필수) | null 처리 |
|---|---|---|---|---|---|
| 1 | 수익률 | `history[]` 기간별 계산 | **토글 적용** (YTD/1M/3M/1Y) | `수익률 ({선택기간})` 동적 치환 | "데이터 부족" |
| 2 | 총 AUM | `etf_holdings_*.csv`의 `market_value_role` 합산 | 현재 시점 | `총 AUM (현재)` 박제 | "—" |
| 3 | Sharpe Ratio | `returns` + `volatility_1y` (연환산) | 1Y 고정 | `Sharpe (1Y)` 박제 | "—" |
| 4 | MDD | `history[].close` rolling_max 기준 | 전체 기간 | `MDD (전체기간)` 박제 | "계산 불가" |
| 5 | 트래킹 에러 | ETF history × 매핑된 벤치마크 history | 1Y 연환산 | `트래킹에러 (1Y)` 박제 | "—" |

**라벨 규칙**: `3-skills-viz.md` "기간 토글 적용 범위" 표 단일 출처. 토글 따라가는 라벨만 동적 치환, 나머지는 기준 하드코딩.

**5번 트래킹에러 색상 판단**:
- < 2% → 🟢 우수 (값 green)
- 2~4% → ⚪ 정상
- > 4% → 🟡 추적력 저하 (값 gold)

**VaR 95%는 KPI에서 제외하고 Step 4 리스크 모니터링 패널로 이동** (`Step 4` 참조).

---

## Step 2: 핵심 차트 2개

### 차트 1 — 누적 수익률 vs 벤치마크 (라인 차트)
- ETF 라인: `#3A9E9E`, 두께 2px
- 벤치마크 라인: `#888780`, 점선 (borderDash: [5,5]), 두께 1px
- 기준일 수익률 = 0% (history[] 첫 번째 날짜)
- X축: 날짜 / Y축: 누적 수익률 %
- 벤치마크 매핑: `references/current-dataset.md`의 ETF 목록 표 기준 (데이터셋 특화)

### 차트 2 — 구성종목 배분 (도넛 차트)
- 데이터: `etf_holdings_[ETF코드].csv` → `name` + `weight_pct`
- 조인 키: `yfinance_ticker` = `market_data ticker`
- 상위 7개 종목 레이블 표시, 나머지 "기타"로 합산
- 색상: `#3A9E9E` 기준 명도 변화 7단계

---

## Step 2.5: 리스크 모니터링 패널 (KPI 카드 하단 신규)

라인차트·도넛차트와 같은 행 또는 그 아래 별도 행에 **리스크 모니터링 카드**를 배치한다.

### 표시 항목
2×2 그리드 + 하단 sparkline:

| 칸 | 지표 | 색상 판단 |
|---|---|---|
| 좌상 | Beta | > 1.2 → gold / < 0.8 → green / 그 외 default |
| 우상 | VaR 95% | < -3% → gold / < -5% → red / 그 외 default |
| 좌하 | 연환산 변동성 | < 15% → green / > 30% → gold / 그 외 default |
| 우하 | 트래킹 에러 | < 2% → green / > 4% → gold / 그 외 default |

### 하단 sparkline
- 라벨: "롤링 변동성 (30D)"
- 차트: 미니 라인차트 (gold `#C8963E` + opacity 0.12 fill)
- 데이터: `2-skills-criteria.md` 롤링 변동성 공식 기준
- 데이터 부족 시: "데이터 부족" 텍스트로 대체

### 레이아웃 위치
- ETF 유형 무관 공통 표시 (패시브/테마형 모두)
- 라인차트(누적수익률) + 도넛차트와 같은 행에 3번째 컬럼 또는 별도 행

---

## Step 3: 보유종목 테이블 + 하단 패널 (ETF 유형별 분기)

### 보유종목 테이블 (공통)
컬럼 순서: 종목명 | 의견 | 비중(%) | 수익률 | **기여도** | **목표주가 괴리**

| 컬럼 | 데이터·계산 | 컬럼 헤더 표기 | 색상 |
|---|---|---|---|
| 종목명 | `name_role` + ticker 뱃지 | `종목명` | `.KS` 없으면 "해외" 뱃지 |
| 의견 | 목표주가 괴리율 기준 (`5-skills-ra.md` 배지 규칙) | `의견` | BUY/HOLD/SELL 배지 |
| 비중(%) | `weight_pct` | `비중(%)` | 1위 > 30% → 행 gold |
| 수익률 | 기간 토글 적용 — `MD.tickers[ticker].returns[기간키]` 사용 (기간키: ytd/1m/3m/1y) | `수익률 ({선택기간})` 동적 치환 | 양수 green / 음수 red |
| **기여도** | `weight_pct × 수익률(기간) / 100` (포트폴리오 수익에 기여한 %p) | `기여도 ({선택기간})` 동적 치환 | 양수 green / 음수 red |
| **목표주가 괴리** | `(target_price - current_price) / current_price × 100` | `목표주가 괴리` | ≥+20% green / ≤-10% red / 그 외 default |

**기간 키 매핑**:
- 토글 `YTD` → `returns.ytd` (없으면 `1m`로 fallback + 디버그 패널 경고)
- 토글 `1M` → `returns.1m`
- 토글 `3M` → `returns.3m`
- 토글 `1Y` → `returns.1y`
- 데이터 없으면 셀 "—"

- 정렬: `weight_pct` 내림차순
- target_price·수익률·obj 누락 시 → "—"
- 행 hover 효과: 배경 `rgba(255,255,255,0.02)`

---

### 하단 패널 — 📌 패시브 ETF: 리밸런싱 신호

`sector_targets.json`의 `etf_targets[ETF코드]`를 로드하여 섹터별 현재-목표 갭을 표시한다.

**섹터 현재 비중 계산**:
- `etf_holdings_[ETF코드].csv`의 holding별 `weight_pct` ×
  `market_data.json`의 `fundamentals.sector`로 섹터 집계
- 매핑 실패 holding → "기타" 섹터로 합산

**갭 계산 및 신호**:
| 조건 | 신호 | 색상 | 표시 |
|---|---|---|---|
| 현재 - 목표 > +`threshold_pct` | 🔴 초과 | `#E24B4A` | "{섹터} {현재}% / 목표 {목표}% → 축소 검토" |
| 현재 - 목표 < -`threshold_pct` | 🟡 부족 | `#C8963E` | "{섹터} {현재}% / 목표 {목표}% → 확대 검토" |
| 범위 내 | 🟢 정상 | `#1D9E75` | "{섹터} {현재}% / 목표 {목표}% — 정상" |

- `threshold_pct`: `sector_targets.json`의 `rebalance_threshold_pct` 값 사용 (기본 5.0%p)
- `sector_targets.json` 없거나 해당 ETF 없으면 → 아래 기존 신호 규칙으로 fallback

**Fallback 리밸런싱 신호** (sector_targets 없을 때):
| 조건 | 신호 | 메시지 |
|---|---|---|
| 1위 종목 weight_pct > 30% | 🟡 | "{종목명} {비중}% 집중 — 분산 검토" |
| MDD < -15% | 🔴 | "리스크 한도 초과 — 포지션 축소 검토" |
| returns.1m > 50% | 🟡 | "단기 {수익률}% 급등 — 차익실현 검토" |
| 조건 없음 | 🟢 | "현재 포트폴리오 정상 범위" |

---

### 하단 패널 — 🎯 테마형 ETF: 집중도 리스크

`sector_targets.json` 미사용. 보유종목 데이터만으로 집중도 리스크를 산출한다.

**표시 지표**:
| 지표 | 계산 | 경고 기준 | 색상 |
|---|---|---|---|
| Top 1 종목 비중 | `weight_pct` 최대값 | > 30% | `#C8963E` |
| Top 3 종목 비중 합 | 상위 3개 `weight_pct` 합산 | > 50% | `#C8963E` |
| Top 5 종목 비중 합 | 상위 5개 `weight_pct` 합산 | > 70% | `#E24B4A` |
| 수익률 기여도 1위 | `weight_pct` × `return_1w_pct` 최대 종목 | — | `#1D9E75` |
| 수익률 기여도 꼴찌 | `weight_pct` × `return_1w_pct` 최소 종목 | — | `#E24B4A` |

- 기여도 표시 형식: "{종목명} {기여도:+.2f}%p"
- 경고 기준 초과 항목은 해당 색상으로 값 강조
- 모든 항목 정상 시 하단에 🟢 "집중도 리스크 정상 범위" 메시지 표시

---

## Quality Check

- [ ] ETF 드롭다운 선택 변경 시 전체 뷰가 재렌더링되는가?
- [ ] ETF 유형(패시브/테마형)이 올바르게 감지되었는가?
- [ ] KPI 카드 4개 모두 렌더링되었는가?
- [ ] MDD 임계값에 따라 카드 테두리 색상이 변경되는가?
- [ ] 벤치마크가 ETF별로 올바르게 매핑되었는가?
- [ ] 1위 종목 30% 초과 시 테이블 행이 gold 강조되는가?
- [ ] 조인 실패 종목이 에러 없이 건너뛰어지는가?
- [ ] 패시브 ETF → 섹터별 목표 대비 갭 패널이 표시되는가?
- [ ] 테마형 ETF → 집중도 리스크 패널이 표시되는가?
- [ ] sector_targets.json 없을 때 fallback 신호로 전환되는가?
- [ ] KPI 카드 라벨이 토글 따라감(`수익률`)과 박제(`Sharpe (1Y)` 등)로 구분되어 표시되는가?
- [ ] 보유종목 테이블의 "수익률"·"기여도" 컬럼 헤더에 선택 기간이 표기되는가?
- [ ] 토글 변경 시 보유종목 테이블의 수익률·기여도가 `returns[기간키]` 기준으로 갱신되는가?
- [ ] 도넛/리스크/리밸런싱 패널 제목에 `(현재 기준)` 또는 `(전체기간)` 기준이 명시되어 있는가?
