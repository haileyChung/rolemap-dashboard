---
name: 2-skills-criteria
description: >
  Use when determining investment analysis standards, calculating financial
  metrics, or making valuation judgments. Defines analysis purpose, metric
  calculation formulas, judgment thresholds, and data interpretation rules.
  Read after 1-skills-data.md, before 3-skills-viz.md.
allowed-tools: Read
---

## 1. 투자 데이터 분석 기준

### 분석 목적 정의
| 뷰 | 핵심 질문 | 판단 기준 |
|---|---|---|
| PM 뷰 | 포트폴리오 전체가 벤치마크 대비 어떤가? | 벤치마크 초과수익 + 리스크 지표 |
| RA 뷰 | 개별 종목이 현재 매수할만한가? | 섹터 평균 대비 밸류에이션 매력도 |

### 기준 기간
- **기본 기간**: **YTD** (연초 대비, 펀드매니저 1차 지표)
- **비교 기간 토글**: YTD / 1M / 3M / 1Y (UI 토글로 전환 가능, 모든 KPI·차트 동시 갱신)
- **기간 명시 필수**: 모든 수치는 KPI 카드/차트 제목에 기간 라벨 표기 (예: "수익률 (YTD)")
- **YTD 계산**: history[] 중 현재 연도 1월 1일 이후 첫 거래일을 기준일로 채택
  - 데이터에 당년 1월 거래일이 없을 경우 → "데이터 부족" 표시 + 1M으로 자동 fallback

### 기준 상수
- **무위험수익률**: 3.5% 연간 (한국 국고채 3년물)
- **월 환산**: 3.5% / 12 = 0.292%
- **거래일 기준**: 연 252일 (월 21일)

---

## 2. PM 지표 계산 규칙

### 수익률 (기간별)
```
YTD 수익률(%) = (현재 close - 당년 1월 첫 거래일 close) / 당년 1월 첫 거래일 close × 100
1M 수익률(%) = (현재 close - 21영업일 전 close) / 21영업일 전 close × 100
3M 수익률(%) = (현재 close - 63영업일 전 close) / 63영업일 전 close × 100
1Y 수익률(%) = returns.1y 직접 사용 또는 252영업일 전 기준 계산
```
- 사용자가 선택한 기간(토글)에 따라 위 공식 중 하나 적용
- 기간별 기준일 close가 없으면 → "데이터 부족" 표시 후 차순위 기간으로 fallback

### MDD (최대 낙폭)
```
rolling_max[i] = max(close[0] ~ close[i])
drawdown[i] = (close[i] - rolling_max[i]) / rolling_max[i] × 100
MDD = min(drawdown[])
```

### Sharpe Ratio
```
daily_return[i] = (close[i] - close[i-1]) / close[i-1]
annual_return = returns.1m × 12
annual_vol = std(daily_return[]) × sqrt(252)
Sharpe = (annual_return - 3.5%) / annual_vol
```

### VaR 95%
```
daily_returns = [daily_return[i] for i in history[]]
VaR_95 = percentile(daily_returns, 5)
표기: "-X.XX%" 형식
```

### 벤치마크 초과수익
```
초과수익 = ETF 누적수익률 - 벤치마크 누적수익률
```

### 트래킹 에러 (Tracking Error)
```
일별 초과수익[i] = ETF daily_return[i] - 벤치마크 daily_return[i]
트래킹 에러 = std(일별 초과수익[]) × sqrt(252) × 100  (연환산 %)
```
- 데이터: ETF history[] + 매핑된 벤치마크 history[]
- 벤치마크 매핑은 `references/current-dataset.md` 참조
- ETF·벤치마크 history 길이가 다를 경우 → 공통 날짜로 정렬 후 계산
- 표시 형식: "X.XX%"
- 판단: 패시브 ETF는 < 4% 권장 (낮을수록 인덱스 추종력 우수)

### Beta (체계적 위험)
```
공분산 = cov(ETF daily_return[], 벤치마크 daily_return[])
분산   = var(벤치마크 daily_return[])
Beta   = 공분산 / 분산
```
- 우선순위: `fundamentals.beta` 있으면 직접 사용, 없으면 위 공식으로 계산
- 데이터 부족(history 30영업일 미만) → "—"
- 표기: "X.XX" (소수점 2자리)
- 판단: 1.0 = 시장과 동일, > 1.2 시장 대비 변동성 큼, < 0.8 방어적

### 연환산 변동성
```
변동성(%) = std(daily_return[]) × sqrt(252) × 100
```
- 우선순위: `volatility_role` (`volatility_1y`) 있으면 직접 사용, 없으면 위 공식
- 표기: "XX.X%"

### 롤링 변동성 (30영업일 이동)
```
rolling_vol[i] = std(daily_return[i-29 ~ i]) × sqrt(252) × 100
```
- 표시: 미니 라인차트 (sparkline 형태, height ~40px)
- 색상: gold (`#C8963E`) 라인 + 그라디언트 fill
- 데이터 부족(40영업일 미만) → 차트 영역에 "데이터 부족" 텍스트만

---

## 3. RA 지표 계산 규칙

### PER
```
PER(선행) = fundamentals.per_fwd   ← 우선 사용
PER(TTM)  = fundamentals.per_ttm   ← per_fwd 없을 때 대체
표기: "X.XX x" 형식
```

### PBR
```
PBR = fundamentals.pbr
표기: "X.XX x" 형식
```

### ROE
```
ROE = fundamentals.roe  ← 우선 사용
    = financial_index[idx_nm="ROE"].idx_val  ← roe 없을 때 대체
표기: "XX.X%" 형식
```

### 목표주가 괴리율
```
괴리율(%) = (target_price - current_price) / current_price × 100
표기: "+XX.X%" / "-XX.X%" 부호 명시
```

### 섹터 평균 PER
```
섹터평균_PER = mean(per_fwd of holdings where sector == 대상섹터)
null 제외 후 계산, 유효 종목 3개 미만이면 "섹터평균 없음" 표시
```

### EPS (TTM)
```
EPS_TTM = fundamentals.eps_ttm  (직접 사용)
표기: "X,XXX원" (콤마 구분)
YoY 변동 표시: 전년 EPS와 비교 → "↑ YoY +XX.X%" 형식
전년 EPS 데이터 없으면 → YoY 표시 생략
```

### 배당수익률
```
배당수익률(%) = fundamentals.dividend_yield  (이미 % 단위)
DPS         = fundamentals.dps               (주당배당금, 원)
표기: "X.X%" + 하단에 "DPS X,XXX원" 보조 표시
null → "—" + DPS도 숨김
```

---

## 4. 투자 판단 기준 (임계값)

### PM 판단 기준 — 색상 및 아이콘 자동 적용
| 지표 | 임계값 | 판단 | 적용 위치 |
|---|---|---|---|
| MDD | < -15% | 🔴 리스크 경고 | KPI 카드 테두리 red + 인사이트 배너 |
| MDD | -15% ~ -5% | 🟡 주의 | KPI 카드 테두리 gold |
| MDD | > -5% | 🟢 정상 | 기본 스타일 |
| Sharpe | > 1.0 | 🟢 우수 | KPI 카드 값 green |
| Sharpe | < 0 | 🔴 손실 | KPI 카드 값 red |
| 초과수익 | > +10%p | 🟢 초과 달성 | 인사이트 배너 |
| 초과수익 | < -10%p | 🔴 하회 | 인사이트 배너 |
| 1위 종목 비중 | > 30% | 🟡 집중 위험 | 테이블 해당 행 gold 강조 |

### RA 판단 기준 — 색상 및 배지 자동 적용
| 지표 | 임계값 | 판단 | 적용 위치 |
|---|---|---|---|
| 목표주가 괴리율 | ≥ +20% | 📈 BUY | 배지 green + 인사이트 배너 |
| 목표주가 괴리율 | -10% ~ +20% | ⚪ HOLD | 배지 gray |
| 목표주가 괴리율 | ≤ -10% | 📉 SELL | 배지 red + 인사이트 배너 |
| PER | < 섹터평균 × 0.8 | 🟢 저평가 | 테이블 셀 green 강조 |
| PER | > 섹터평균 × 1.2 | 🔴 고평가 | 테이블 셀 red 강조 |
| ROE | > 15% | 🟢 우수 | KPI 카드 값 green |
| ROE | < 5% | 🔴 낮음 | KPI 카드 값 red |
| 부채비율 | > 200% | 🟡 주의 | 재무패널 해당 항목 gold |
| 부채비율 | > 400% | 🔴 위험 | 재무패널 해당 항목 red |

---

## 5. 데이터 해석 기준

- ETF 1M 수익률 80%+ → 레버리지 ETF 정상값, 이상값 마킹 금지
- 연속 동일 종가 → yfinance forward-fill (한국 공휴일), 정상 처리
- `idx_val` 최신 연도 우선 (2023 → 2022 → 2021 순)
- 금융업 종목 (은행·보험·증권) → 부채비율 판단 기준 적용 제외

---

## Quality Check

- [ ] 무위험수익률 3.5% 연간 기준으로 적용되었는가?
- [ ] MDD가 rolling_max 기준으로 계산되었는가?
- [ ] PM 판단 기준이 KPI 카드 색상에 반영되었는가?
- [ ] RA 판단 기준이 테이블 셀 색상 + 배지에 반영되었는가?
- [ ] 섹터 평균 PER이 null 제외 후 계산되었는가?
- [ ] 금융업 종목의 부채비율 판단이 제외되었는가?
