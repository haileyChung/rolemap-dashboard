---
name: current-dataset
description: >
  Dataset-specific metadata for the current Korean ETF + holdings data.
  Loaded on-demand. Replace this file when switching datasets — universal
  rules in 1-skills-data.md and references/role-catalog.md remain unchanged.
allowed-tools: Read
---

# 현재 데이터셋 메타정보

⚠️ **이 파일은 현재 데이터셋(한국 ETF + KOSPI 보유종목) 한정.**
다른 데이터로 교체 시 이 파일만 새로 작성하면 쉽게 적용 가능. 다른 Skills 파일은 그대로.

---

## 데이터 파일 목록

| 파일 | 형식 | 용도 |
|---|---|---|
| `데이터/market_data.json` | JSON | ETF + holdings 시세·펀더멘털·분기실적 |
| `데이터/etf_holdings_*.csv` | CSV (5개) | ETF별 구성종목·비중 |
| `데이터/financial_index.json` | JSON (long-format) | 종목별 재무지표 65종 |
| `데이터/sector_targets.json` | JSON (더미) | ETF별 섹터 목표 비중 |
| `데이터/consensus_data.json` | JSON (더미) | 종목별 분기 컨센서스 vs 실제 |

---

## ETF 목록 + 분류 + 벤치마크

| 코드 | 한글명 | 벤치마크 키 | 유형 |
|---|---|---|---|
| `423920.KS` | TIGER 미국필라델피아반도체나스닥 | `^SOX` | 📌 패시브 |
| `412570.KS` | TIGER 2차전지테마 | `^KQ11` | 🎯 테마형 |
| `123320.KS` | TIGER 코스피200 | `^KS200` | 📌 패시브 |
| `243880.KS` | TIGER 반도체 | `^KS200` | 📌 패시브 |

**기본 선택값**:
- PM 드롭다운 기본: `423920.KS`
- RA 드롭다운 기본: `006400.KS` (삼성SDI)

---

## ticker 형식 변환 규칙 (현재 데이터 한정)

| 파일 | ticker 형식 | 변환 |
|---|---|---|
| `market_data.json` 키 | `{6자리}.KS` 또는 해외코드 | 그대로 사용 |
| `financial_index.json.ticker` | `{6자리}.KS` | 그대로 사용 |
| `etf_holdings_*.csv.ticker` | 숫자만 (앞 0 누락 가능) | **단독 사용 금지** |
| `etf_holdings_*.csv.yfinance_ticker` | `{6자리}.KS` | 보유종목 조인 키로 사용 |
| `etf_holdings_*.csv` **파일명**의 ETF 코드 | `{6자리}` (`.KS` 없음, 예: `etf_holdings_423920.csv`) | **메모리 컬렉션의 키로 쓸 때 `.KS` 부착 필수** (예: `HOLDINGS["423920.KS"]`) |

**조인 규칙**:
- 모든 파일은 **`yfinance_ticker` = `market_data ticker 키`** 기준으로 조인 (보유종목 → 종목 정보).
- ETF별 보유종목 묶음을 메모리 객체(`HOLDINGS` 등)로 보관할 때, **키는 ETF의 `market_data ticker 키 형식`(`{6자리}.KS`)으로 통일**한다. 파일명에서 추출한 6자리 코드를 그대로 쓰면 ETF 드롭다운 값(`423920.KS`)과 키가 어긋나 보유종목·도넛이 빈 데이터로 렌더링된다.

---

## 데이터 특이사항 (알려진 이슈)

### 깨진 short_name (4건)
yfinance 데이터 이슈로 short_name이 `{ticker},{영숫자},{숫자}` 형식으로 들어옴:
- `086520.KS` (실제: 에코프로)
- `247540.KS` (실제: 에코프로비엠)
- `033100.KS` (실제: 한화생명)
- `060370.KS` (실제: LS마린솔루션)

→ Skills 규칙: 이름 깨진 종목은 ticker 코드 그대로 표시 (한글명 임의 부여 금지).

### 정상이지만 콤마 포함된 이름 (1건)
- `006400.KS` short_name = `"SAMSUNG SDI CO.,LTD."` ← 정상 사명, 그대로 사용

### 영업이익 0인 금융업 (17건)
Financial Services 섹터 종목들은 `quarterly[].op_income = 0` (수익 구조 차이).
→ Skills 규칙: `is_financial: true` 시 영업이익 서프라이즈 미산출.

### 해외 holding (1건)
- `SOXQ` (Invesco PHLX Semiconductor ETF) — 미국 상장, `.KS` 없음
- → "해외" 레이블 표시

---

## RA 드롭다운 제외 키워드

ETF/인덱스 성격 holding을 RA 리스트에서 제외할 때 `short_name`에서 검색할 키워드:

```
TIGER, KODEX, KINDEX, HANARO, ARIRANG, KOSEF, FOCUS, SOL, ACE, TREX, TIMEFOLIO,
Invesco, iShares, SPDR, ETF
```

**현재 데이터 기준 제외 대상 4건**: `SOXQ`, `364980.KS`, `102110.KS`, `139260.KS`

---

## ETF 유형 분류 키워드 (패시브 vs 테마형)

**패시브** 인식 (tracking_index 또는 ETF명에 포함):
```
PHLX, S&P, NASDAQ, 코스피, KS200, KQ11, 반도체, Semiconductor
```

**테마형** 인식:
```
테마, TOP, Theme
또는 tracking_index 자체가 없을 때
```

판별 결과는 위 ETF 목록 표 참조.
