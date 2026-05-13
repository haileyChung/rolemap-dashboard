---
name: role-catalog
description: >
  Role-based column synonym dictionary. Loaded on-demand by 1-skills-data.md
  during data discovery (Step 1). Each role lists candidate column/key names
  in priority order — first match wins.
allowed-tools: Read
---

# 역할 카탈로그 (Role Catalog)

데이터 스캔 시 각 파일의 컬럼명·JSON 키를 아래 후보와 순서대로 매칭한다.
**첫 매칭을 채택**하고 콘솔에 매핑 결과를 로그로 남긴다.

대소문자·공백·언더스코어/하이픈 차이는 정규화 후 비교 (`Close_Price` = `closeprice`).

---

## 1. 식별·조인 역할

| 역할 | 필수 | 인식 후보 (우선순위) | 검증 |
|---|---|---|---|
| `ticker_role` | ✅ | yfinance_ticker, ticker, Ticker, 종목코드, 코드, code, symbol, isin | 비어있지 않음 |
| `name_role` | ⚪ | name, 종목명, short_name, 이름, long_name, fullname | string |
| `sector_role` | ⚪ | sector, Sector, 섹터, industry, gics_sector | string |
| `role_field` | ⚪ | role, type, kind, category | "etf"/"holding" 등 |

---

## 2. 가격·수익률 역할

| 역할 | 필수 | 인식 후보 | 단위/검증 |
|---|---|---|---|
| `close_role` | ✅ (시세 차트) | close, Close, 종가, adj_close, current_price, 현재가, 가격, last_price, last, px_last, price | number > 0 |
| `history_role` | ✅ (시계열) | history, prices, price_history, 시계열, daily, ohlc | array |
| `date_role` | ✅ (history 내) | date, Date, 날짜, 일자, timestamp, time, dt | YYYY-MM-DD |
| `volume_role` | ⚪ | volume, Volume, 거래량, vol | number ≥ 0 |
| `return_role` | ⚪ | returns, return, 수익률, pnl, performance, total_return | object/number |
| `volatility_role` | ⚪ | volatility, vol_1y, 변동성, std_dev, sigma | number ≥ 0 (%) |

**`return_role` 하위 기간 키**: `1d, 1w, 1m, 3m, 6m, 1y, ytd` (없는 기간은 null)

---

## 3. 비중·금액 역할

| 역할 | 필수 | 인식 후보 | 단위 자동 인식 |
|---|---|---|---|
| `weight_role` | ✅ (PM) | weight_pct, weight, Weight, 비중, allocation | % (0~100) |
| `amount_role` | ⚪ | market_value, market_value_krw, mv, 평가금액, value | 컬럼명 suffix로 통화 추정 |
| `quantity_role` | ⚪ | quantity, qty, shares, 수량 | number ≥ 0 |

**금액 단위 자동 추정 규칙**:
- 컬럼명에 `_krw`/`원`/`KRW` 포함 → 원 단위
- 컬럼명에 `_eok`/`억` 포함 → 억원 단위
- 컬럼명에 `_usd`/`$` 포함 → 달러
- 미상 → 첫 5개 값의 자릿수 추정 (≥ 1e9 → 원, 1e2~1e4 → 억원)

---

## 4. 펀더멘털·밸류에이션 역할

| 역할 | 필수 | 인식 후보 |
|---|---|---|
| `per_role` | ✅ (RA) | per_fwd, per_ttm, per, PER, 주가수익비율, p_e, pe_ratio |
| `pbr_role` | ✅ (RA) | pbr, PBR, 주가순자산비율, p_b, pb_ratio |
| `eps_role` | ⚪ | eps_ttm, eps, EPS, 주당순이익 |
| `bps_role` | ⚪ | bps, BPS, 주당순자산 |
| `roe_role` | ⚪ | roe, ROE, 자기자본이익률 |
| `op_margin_role` | ⚪ | op_margin, operating_margin, 영업이익률 |
| `target_price_role` | ⚪ | target_price, target, 목표주가, price_target |
| `dividend_yield_role` | ⚪ | dividend_yield, div_yield, 배당수익률 |
| `dps_role` | ⚪ | dps, DPS, 주당배당금 |
| `beta_role` | ⚪ | beta, Beta, 베타 |
| `market_cap_role` | ⚪ | market_cap, mcap, 시가총액 |

---

## 5. 분기 실적 역할

| 역할 | 필수 | 인식 후보 |
|---|---|---|
| `quarterly_role` | ⚪ | quarterly, quarters, 분기실적, financial_history |
| `fiscal_quarter_role` | (내부) | quarter, Q, 분기, period |
| `revenue_role` | ⚪ | revenue, sales, 매출, 매출액, total_revenue |
| `op_income_role` | ⚪ | op_income, operating_income, 영업이익, ebit |
| `net_income_role` | ⚪ | net_income, profit, 순이익, 당기순이익 |

**컨센서스 데이터** (별도 파일로 제공 시):
| 역할 | 인식 후보 |
|---|---|
| `consensus_revenue_role` | consensus_revenue, est_revenue, 컨센서스매출 |
| `consensus_op_role` | consensus_op_income, est_op, 컨센서스영업이익 |
| `surprise_pct_role` | surprise_pct, revenue_surprise_pct, 서프라이즈율 |

---

## 6. 벤치마크·지수 역할

| 역할 | 필수 | 인식 후보 |
|---|---|---|
| `benchmark_root` | ⚪ | benchmarks, indices, 지수, market_index |
| `benchmark_history_role` | (내부) | history (벤치마크 객체 내) |
| `tracking_index_role` | ⚪ | tracking_index, benchmark, 추종지수 |

벤치마크 키 자체(예: `^SOX`, `^KS200`)와 ETF→벤치마크 매핑은 **데이터셋 특화 정보**(`current-dataset.md`) 참조.

---

## 7. 재무지표 시리즈 (financial_index 형식)

`{ticker, idx_nm, idx_val, bsns_year}` 형태의 long-format 재무지표 데이터:

| 역할 | 인식 후보 |
|---|---|
| `account_name_role` | idx_nm, account_name, 지표명, metric_name |
| `current_value_role` | idx_val, value, 지표값 (문자열이면 parseFloat) |
| `fiscal_year_role` | bsns_year, year, 사업연도, fiscal_year |

---

## 매칭 실패 처리

| 상황 | 처리 |
|---|---|
| 필수 역할 매칭 실패 | 콘솔 경고 + 해당 차트/KPI 비활성화 (전체 중단 금지) |
| 선택 역할 매칭 실패 | 해당 항목만 "—" 표시, 정상 진행 |
| 중복 매칭 (같은 데이터에 여러 후보 존재) | 우선순위 첫 번째 채택, 나머지는 콘솔 로그만 |
