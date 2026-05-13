---
name: 1-skills-data
description: >
  Universal data discovery + role-based column mapping for investment data.
  Use when CSV/JSON investment data files are uploaded. Always run after
  0-skills-guide.md and before all other skills files. Detects data structure,
  resolves role keys via on-demand role catalog, and applies preprocessing.
allowed-tools: Read, Glob
---

## 핵심 철학

**컬럼명에 의존하지 않는다.** 같은 의미의 데이터는 이름이 달라도(예: `close` / `종가` / `Close_Price`) 동일한 **역할(role)** 로 인식한다.

데이터셋이 바뀌어도 이 파일은 그대로 작동한다. 데이터 특화 정보는 `references/current-dataset.md` 및 `references/role-catalog.md`에 분리되어 있다.

---

## 실행 환경 요건

- 데이터 **파싱·변환·계산**: Python·Bash 사용 금지 → 100% JavaScript (브라우저 런타임)
- 단, 루트의 **`build_dashboard.py` 단일 파일**은 raw 텍스트 인라인 어셈블리 용도로만 허용 (`0-skills-guide.md` "빌드 방식" 참조). 그 외 보조 Python 파일 생성 금지.
- CSV: `split('\n')` → `split(',')` → `trim()` → BOM 제거 (charCode 0xFEFF)
- JSON: `JSON.parse()`
- 경로: 상대경로 `데이터/` 폴더 (한글 경로 허용)

---

## Step 0: 데이터셋 적합성 판정 (Fast Path vs Fallback)

매핑 시작 전 `references/current-dataset.md`가 실제 데이터와 일치하는지 검증해
**하드코딩 경로**(빠름)와 **role-catalog 동적 매칭 경로**(범용) 중 하나를 선택한다.

### 0.1 적합성 체크 (모두 통과해야 Fast Path)

| # | 체크 항목 | 판정 기준 |
|---|---|---|
| 1 | ETF 목록 일치 | `current-dataset.md` "ETF 목록 + 분류 + 벤치마크" 표의 ticker가 모두 `market_data.json`에 존재 |
| 2 | ticker 형식 일치 | `etf_holdings_*.csv`의 `yfinance_ticker` 형식이 `market_data.json` 키 형식과 동일 |
| 3 | 핵심 컬럼 존재 | 핵심 역할 컬럼명(`history`, `fundamentals`, `weight_pct`, `per_fwd`, `target_price`)이 명시된 이름 그대로 존재 |
| 4 | 벤치마크 키 존재 | `current-dataset.md`에 명시된 벤치마크 키(`^SOX`, `^KQ11`, `^KS200`)가 `market_data.benchmarks`에 존재 |

### 0.2 분기 처리

**✅ Fast Path** (4개 모두 통과):
- `current-dataset.md` 기반 하드코딩 매핑 사용
- 콘솔/디버그 패널: `[role-map] PATH=fast-path (current-dataset.md 일치)`

**🔄 Fallback Path** (1개 이상 실패):
- `references/role-catalog.md`의 후보 리스트로 동적 매칭 (Step 1.2)
- 실패 사유 콘솔 + 디버그 패널에 명시:
  ```
  [role-map] PATH=fallback (reason: missing ETFs 423920.KS, schema mismatch)
  [role-map] FALLBACK to role-catalog dynamic matching
  ```
- 적용 결과를 디버그 패널 "역할 매핑" 섹션에 표시 (Fast Path와 동일 형식)

### 0.3 부분 fallback 허용

전체-or-nothing 아닌 **역할별 독립 fallback** 가능:
- ETF 목록은 일치하지만 새 컬럼이 추가된 경우 → 기존 역할은 Fast Path, 새 역할만 role-catalog 동적 매칭
- 디버그 패널에서 역할별로 `(fast)` / `(catalog)` 출처 표시

### 0.4 설계 원칙

| 원칙 | 의미 |
|---|---|
| **Fast Path 우선** | 일치하면 항상 하드코딩 사용 (예측 가능·빠름) |
| **자동 감지** | 사용자에게 묻지 않고 코드가 판정 |
| **실패 시 graceful** | role-catalog로 자동 전환, 전체 중단 금지 |
| **투명성** | 어느 경로를 썼는지 콘솔·디버그 패널에 항상 표시 |

### 0.5 구현 의사코드 (AI가 그대로 변환 가능)

AI가 이 명세를 읽고 JS로 구현할 때 아래 의사코드를 그대로 따른다:

```javascript
function detectDatasetFit(MD, HOLDINGS, currentDatasetMeta) {
  const reasons = [];

  // 체크 1: ETF 목록 일치
  const expectedETFs = currentDatasetMeta.etfList.map(e => e.code);
  const missing = expectedETFs.filter(t => !MD.tickers[t]);
  if (missing.length > 0) {
    reasons.push(`missing ETFs: ${missing.join(',')}`);
  }

  // 체크 2: ticker 형식 일치 (CSV yfinance_ticker가 market_data 키와 같은 형식인가)
  for (const [code, rows] of Object.entries(HOLDINGS)) {
    if (!rows.length) continue;
    const yt = rows[0].yfinance_ticker || '';
    const isInMD = !!MD.tickers[yt];
    const sampleMDKey = Object.keys(MD.tickers)[0];
    const sameSuffix = yt.includes('.') === sampleMDKey.includes('.');
    if (!sameSuffix) {
      reasons.push(`ticker format mismatch in ${code}`);
      break;
    }
  }

  // 체크 3: 핵심 컬럼 존재
  const sample = Object.values(MD.tickers)[0] || {};
  const requiredKeys = ['history', 'fundamentals'];
  const missingKeys = requiredKeys.filter(k => !(k in sample));
  if (missingKeys.length > 0) {
    reasons.push(`schema missing: ${missingKeys.join(',')}`);
  }

  // 체크 4: 벤치마크 키 존재
  const expectedBenches = currentDatasetMeta.benchmarks; // ['^SOX','^KQ11','^KS200']
  const missingBench = expectedBenches.filter(b => !MD.benchmarks?.[b]);
  if (missingBench.length > 0) {
    reasons.push(`missing benchmarks: ${missingBench.join(',')}`);
  }

  return {
    fit: reasons.length === 0,
    reasons,
    path: reasons.length === 0 ? 'fast-path' : 'fallback'
  };
}

// 사용
const fitCheck = detectDatasetFit(MD, HOLDINGS, CURRENT_DATASET_META);
console.log(`[role-map] PATH=${fitCheck.path}`,
  fitCheck.fit ? '(current-dataset.md 일치)' : `(reason: ${fitCheck.reasons.join('; ')})`);

if (fitCheck.fit) {
  applyHardcodedMapping();   // current-dataset.md 기반 직접 참조
} else {
  applyRoleCatalogMapping(); // role-catalog.md 후보 리스트 순회 매칭
}
```

**중요**: 위 의사코드는 **참고 구조**이며, AI는 의미를 보존하면서 자유롭게 재구성할 수 있다. 단 다음은 필수:
- 4개 체크 모두 실행
- `[role-map] PATH=...` 로그 출력
- 분기 결과를 디버그 패널에 표시 (`6-skills-report.md` Step 4)

---

## Step 1: 데이터 자동 감지 (Discovery)

데이터 파일을 스캔해 컬럼/JSON 키를 **역할(role)** 로 매핑한다.

### 1.1 스캔
- `데이터/` 폴더의 모든 CSV/JSON 파일 로드
- CSV → 헤더 행 추출 / JSON → 최상위 키 + 중첩 키 재귀 추출

### 1.2 매칭
- 각 키를 `references/role-catalog.md`의 후보 리스트와 **우선순위 순**으로 매칭
- **정규화 규칙** (비교 전 양쪽에 동일 적용):
  ```
  s.toLowerCase()
   .replace(/[\s_\-]+/g, '')   // 공백·언더스코어·하이픈 제거
   .replace(/^﻿/, '')           // BOM 제거
  ```
  → `Close_Price` ↔ `close-price` ↔ `CLOSE PRICE` 모두 `closeprice`로 통일
- **매칭 기준**: 정확히 일치 (exact match). **부분 일치·정규식·접두/접미 매칭 금지**
- **키워드 매칭** (RA 제외 키워드 등 별도 명시된 곳):
  - 정규화 후 `includes()` (부분 문자열 검사)
  - 키워드 자체도 동일하게 정규화
- **첫 매칭 채택**, 나머지 후보는 무시 (디버그 패널에 "다른 후보 있었으나 우선순위에서 밀림" INFO 로그)

### 1.3 로깅
콘솔에 매핑 결과 출력 (디버깅용):
```
[role-map] close_role  ← current_price (market_data.json)
[role-map] weight_role ← weight_pct    (etf_holdings_*.csv)
[role-map] per_role    ← per_fwd       (market_data.json)
[role-map] WARN: target_price_role 매칭 실패 → RA 목표주가 패널 비활성화
```

### 1.4 가용성 판정
- **필수 역할 매칭 실패** → 해당 차트/KPI 비활성화 (전체 중단 금지)
- **선택 역할 매칭 실패** → 해당 항목만 "—" 표시
- 카탈로그 상세는 `references/role-catalog.md` 참조

---

## Step 2: 조인 키 규칙 (범용)

서로 다른 파일을 결합할 때:

### 2.1 조인 키 우선순위 (첫 매칭 채택)
후보 리스트를 우선순위 순으로 시도:
1. `ticker_role` (`role-catalog.md`의 ticker_role 매핑 결과)
2. `isin_role` (있으면 — `role-catalog.md`에 추가 필요)
3. 종목명 (정규화 후 — fallback 전용)

### 2.2 형식 정규화
- 동일 키가 여러 형식으로 존재하면, **데이터 카운트가 가장 많은 형식**을 정규형으로 채택
  (단순 길이 휴리스틱 대신, 실제 분포 기반)
- 변환 규칙은 `references/current-dataset.md`의 "ticker 형식 변환 규칙" 참조
  → 데이터셋 교체 시 이 규칙도 갱신 필수

### 2.3 매칭 실패 처리
- 매칭 실패 항목 → 콘솔/디버그 패널 경고, 건너뛰기 (에러 중단 금지)
- 매칭 실패율이 20% 초과 시 → 디버그 패널에 RED 경고 ("조인 키 부적합 — current-dataset.md 검토 필요")

### 2.4 그룹별 독립 처리
- 데이터 구조상 그룹(예: ETF, 포트폴리오, 인덱스 등)이 존재하면, 그룹별로 조인을 독립 수행
- 같은 종목이 여러 그룹에 속해도 각 그룹 컨텍스트 유지

### 2.5 그룹 컬렉션 키 정규화 (필수)
ETF별 보유종목·섹터별 종목 등 **그룹별 묶음을 메모리 객체로 보관할 때, 그룹 키는 그룹 자체의 `ticker_role` 정규형과 동일한 형식**이어야 한다.

| 상황 | 잘못된 예 | 올바른 예 |
|---|---|---|
| ETF 보유종목 컬렉션 키 | 파일명에서 추출한 코드 그대로 (`HOLDINGS["423920"]`) | ETF ticker 키 형식과 일치 (`HOLDINGS["423920.KS"]`) |

**근거**: ETF 드롭다운·차트·테이블이 `market_data` 키 형식(`{6자리}.KS`)으로 컬렉션을 조회하므로, 컬렉션 키가 다르면 `undefined`가 돼서 도넛/보유종목 등이 **에러 없이 빈 데이터로 렌더링**된다 (디버깅하기 매우 어려운 무증상 버그).

데이터셋별 구체적 변환 규칙은 `references/current-dataset.md`의 "ticker 형식 변환 규칙" 표 마지막 행 참조.

**현재 데이터셋의 구체적 ticker 형식 변환 규칙**: `references/current-dataset.md` 참조.

---

## Step 3: PM / RA 뷰 자동 분기

### PM 뷰 진입 조건
`role_field`가 `"etf"`인 종목 또는 `weight_role` + `history_role` 조합 보유.

### RA 뷰 진입 조건
`role_field`가 `"holding"`인 종목 또는 `per_role`/`pbr_role` 보유.

### RA 드롭다운 제외 기준 (3가지 모두 적용)

| 조건 | 처리 |
|---|---|
| **A** `name_role` 값에 ETF/인덱스 키워드 포함 | 드롭다운에서 **제외** |
| **B** `per_role`, `pbr_role`, `target_price_role` 모두 null + `quarterly_role` 빈 배열 | 드롭다운에서 **제외** |
| **C** `name_role`이 `{ticker},{영숫자},{숫자}` 패턴(이름 깨짐) | 제외 안 함, 표시명만 ticker로 대체 |

키워드 목록 + 현재 데이터셋 적용 결과: `references/current-dataset.md` 참조.

### ETF 유형 분류 (패시브 vs 테마형)
PM 뷰 하단 패널 분기에 사용 (`4-skills-pm.md` Step 3 참조).

| 유형 | 판별 기준 |
|---|---|
| 📌 패시브 | `tracking_index_role` 존재 + 키워드 매칭 OR ETF명에 시장지수명 포함 |
| 🎯 테마형 | 위 조건 미충족 (특히 ETF명에 "테마"/"TOP"/"Theme" 또는 tracking_index 없음) |

키워드 목록 + 현재 데이터셋 분류 결과: `references/current-dataset.md` 참조.

---

## Step 4: 전처리 규칙

| 규칙 | 처리 |
|---|---|
| `current_value_role` 문자열 형식 | `parseFloat()` 변환 필수 (financial_index 형태) |
| null 수치 (가격·지표) | 표시는 "—", 계산에서 제외 (NaN 전파 금지) |
| **결측 비중 (`weight_role` null)** | **0으로 채움** (도넛/테이블 합계 일관성 유지) |
| 금액 단위 | `references/role-catalog.md` "단위 자동 추정" 규칙 적용, 표시는 억원 통일 |
| 이상값 (수익률 ±50% 초과) | 마킹만, 자동 제거 금지 (레버리지 ETF 정상값일 수 있음) |
| 날짜 누락 | 직전 영업일로 forward-fill |
| 한글 인코딩 | 모든 파일 UTF-8 강제 |

---

## Quality Check

- [ ] **Step 0 적합성 체크 4개**가 실행되어 Fast Path / Fallback이 결정되었는가?
- [ ] Fast Path / Fallback 선택 결과가 콘솔·디버그 패널에 표시되었는가?
- [ ] Fallback 시 실패 사유가 명시되었는가?
- [ ] 모든 데이터 파일이 UTF-8로 로드되었는가?
- [ ] Step 1.3 콘솔 로그에 모든 필수 역할이 매핑되었는가?
- [ ] 매칭 실패한 역할은 경고 후 그래프 비활성화로 처리되었는가? (전체 중단 금지)
- [ ] ticker 조인 키가 정규형으로 통일되었는가?
- [ ] **그룹 컬렉션(예: `HOLDINGS`)의 키가 그룹 자체의 ticker 키 형식과 일치하는가?** (Step 2.5 — 파일명 코드 단독 사용 금지)
- [ ] RA 제외 기준 A·B·C가 적용되었는가?
- [ ] ETF가 패시브/테마형으로 분류되었는가?
- [ ] 데이터셋 특화 규칙은 `references/current-dataset.md`에서 가져왔는가? (하드코딩 금지)
