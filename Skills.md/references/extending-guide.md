---
name: extending-guide
description: >
  Guide for extending the system to new datasets, new asset classes
  (bonds, options, commodities, real estate, FX), new markets, and new
  view types. Read when the user wants to apply this Skills system to
  data that is not Korean equities + ETFs. References-only — does not
  alter Step 1-4 universal rules.
allowed-tools: Read
---

# 확장 가이드 — 새 데이터·새 자산군·새 시장 적용

이 시스템은 **한국 주식 + ETF**에 최적화되어 있지만, 설계상 다른 자산군·시장에도 확장 가능하다. 본 파일은 확장 시 **어디를 어떻게 갈아끼우는지**를 명시한다. 핵심 원칙: **Step 1~4 범용 규칙은 그대로, 특화 정보(`current-dataset.md`)와 도메인 뷰(PM/RA)만 교체**.

---

## 1. 확장 시나리오별 작업 매트릭스

| 시나리오 | 데이터 교체 | role-catalog 추가 | current-dataset 갱신 | 새 뷰 추가 | 인사이트 템플릿 추가 |
|---|---|---|---|---|---|
| 한국 주식·ETF (현재) | — | — | — | — | — |
| 미국 주식·ETF | ✅ | ⚪ | ✅ | — | ⚪ |
| 글로벌 멀티마켓 | ✅ | ⚪ | ✅ (다중) | — | ⚪ |
| 채권 | ✅ | ✅ (만기·쿠폰·신용등급) | ✅ | ✅ (Fixed Income 뷰) | ✅ |
| 옵션·선물 | ✅ | ✅ (행사가·만기·델타) | ✅ | ✅ (Derivatives 뷰) | ✅ |
| 원자재 | ✅ | ✅ (인도월·창고비) | ✅ | ✅ (Commodity 뷰) | ✅ |
| 부동산·리츠 | ✅ | ✅ (NAV·LTV·점유율) | ✅ | ✅ (REITs 뷰) | ✅ |
| 가상자산 | ✅ | ✅ (24h volume·시총 점유율) | ✅ | ✅ (Crypto 뷰) | ✅ |
| 포트폴리오 비교 | ⚪ | — | ⚪ | ✅ (Multi-Portfolio 뷰) | ⚪ |

✅ 필수 / ⚪ 선택 / — 불필요

---

## 2. 단계별 확장 절차 (체크리스트)

### Step 1. 데이터 적합성 진단 (`1-skills-data.md` Step 0 활용)

기존 시스템에 새 데이터를 그대로 넣고 실행:
- Fast Path 통과 → 추가 작업 거의 없음
- Fallback 발생 → 콘솔/디버그 패널 사유 확인

### Step 2. `references/current-dataset.md` 갱신

새 데이터셋의 메타정보를 기재. **Skills.md 본체 파일은 건드리지 않는다.**

필수 갱신 항목:
- 데이터 파일 목록·용도
- 그룹 목록 (ETF 목록 / 포트폴리오 목록 / 채권 발행자 목록 등)
- 벤치마크 매핑
- ticker 형식 변환 규칙
- 알려진 이슈 (깨진 이름, null 패턴, 도메인 특이사항)
- 드롭다운 제외 키워드

### Step 3. `references/role-catalog.md` 후보 추가 (필요 시)

새 자산군에서 신규 역할이 등장하면 카탈로그에 추가. 기존 역할은 그대로.

**예: 채권 추가 시 새 역할**

```markdown
## 8. 채권 전용 역할

| 역할 | 인식 후보 |
|---|---|
| `maturity_role` | maturity, maturity_date, 만기일, 상환일 |
| `coupon_role` | coupon, coupon_rate, 쿠폰, 표면금리 |
| `ytm_role` | ytm, yield_to_maturity, 만기수익률 |
| `duration_role` | duration, modified_duration, 듀레이션 |
| `credit_rating_role` | credit_rating, rating, 신용등급 |
```

### Step 4. 새 뷰 정의 (자산군이 본질적으로 다를 때)

PM 뷰·RA 뷰만으로 표현 불가능한 자산군은 **새 뷰 파일**을 추가:
- 파일 명명: `7-skills-{view-name}.md`, `8-skills-...` (번호 연속)
- frontmatter는 기존 파일과 동일 형식
- 내부 구조도 PM/RA 뷰와 평행 (KPI → 차트 → 패널 → 테이블)

**자산군별 권장 뷰 구성**:

| 자산군 | 권장 KPI 5개 | 핵심 차트 |
|---|---|---|
| 채권 | YTM / 듀레이션 / 컨벡시티 / 신용등급 / 만기수익률 스프레드 | YTM 곡선, 만기 분포, 신용등급 도넛 |
| 옵션 | 델타 / 감마 / 베가 / 세타 / IV | 페이오프 다이어그램, 그릭스 표면 |
| 원자재 | 현물가 / 선물 베이시스 / 콘탱고 / 재고 / 변동성 | 선물 곡선, 재고 추이 |
| 리츠 | 배당수익률 / NAV 디스카운트 / LTV / FFO / 점유율 | NAV 추이, 자산 구성, 임대료 추이 |

### Step 5. `references/insight-templates.md` 메시지 추가

새 자산군의 임계값 기반 메시지를 본 파일 §2~5 형식으로 추가:
- 변수 사전(§1)에 자산군 변수 추가 (예: `{ytmPct}`, `{durationYears}`)
- 트리거 조건 + 색상 토큰 + 메시지 템플릿 표

### Step 6. `0-skills-guide.md` 파일 로딩 표 갱신

새 뷰 파일을 로딩 순서에 추가.

---

## 3. 시장(market) 확장

### 한국 → 미국·유럽·일본·중국·신흥국

대부분 **`current-dataset.md`만 갱신**:
- ticker 형식 변환 규칙: 미국 `AAPL`, 유럽 `BMW.DE`, 일본 `7203.T`, 중국 `600519.SS`
- 벤치마크 키 매핑: `^GSPC`(S&P500), `^STOXX50E`, `^N225`, `000300.SS`
- 통화 단위: `currency` 필드 추가 (`KRW`/`USD`/`EUR`/`JPY`/`CNY`)
- 거래일 캘린더 차이: 휴일 forward-fill 시 시장별 캘린더 사용 (선택)

### 글로벌 다중 시장

- 통화 환산 레이어 추가 (`fx_rates_role` 필요 — role-catalog 추가)
- 표시 통화 토글 (KRW/USD)
- 인사이트 메시지에 `{currency}` 변수 추가

---

## 4. 데이터 구조 확장

### CSV가 아닌 형식 (Parquet, Excel)

본 시스템은 **브라우저 직접 파싱**이 원칙이라 CSV/JSON 외 형식은 권장하지 않는다. 부득이한 경우:
- `build_dashboard.py` 단일 파일에서 raw 텍스트로 변환 (어셈블리 단계, **데이터 변환 금지** 원칙 유지)
- 또는 데이터 제공자에게 CSV/JSON 형식 요청

### 실시간 데이터 (WebSocket, REST API)

- `fetch()` 금지 원칙(Step 1) 그대로 — 빌드 시 스냅샷 인라인
- 실시간이 필요하면 별도 서비스 레이어 (본 시스템 범위 외)

### 매우 큰 데이터셋 (>100MB)

- 단일 HTML 인라인은 한계 (브라우저 파싱 부담)
- 권장: Top-N 종목만 인라인, 나머지는 lazy-load (Skills 명세에 미포함 — 사용자 정의)

---

## 5. 뷰 추가 시 디자인 일관성 체크리스트

새 뷰를 만들 때 기존 PM/RA 뷰와 동일 시각 정체성을 유지:

- [ ] 색상 토큰은 `references/design-tokens.md` 참조 (hex 직접 사용 금지)
- [ ] KPI 5개 카드 + 인사이트 배너 + 차트 그리드 + 테이블 패턴 따름
- [ ] 기간 토글 (YTD/1M/3M/1Y) 적용 — 시계열이 있다면 필수
- [ ] 임계값 기반 조건부 색상 적용
- [ ] 자동 인사이트 메시지 템플릿화 (`insight-templates.md`)
- [ ] 디버그 패널에 새 뷰의 매핑 상태 추가
- [ ] null·데이터 부족 케이스 처리 ("—" 표시, 차트 비활성화)

---

## 6. 후방 호환성 (Backward Compatibility)

확장 작업 시:
- ❌ 기존 `role-catalog.md`의 역할 이름 변경 금지 (다른 데이터셋이 의존)
- ❌ 기존 KPI 정의·임계값 변경 금지 (`2-skills-criteria.md`)
- ✅ 새 역할·새 임계값·새 뷰는 **추가**만 가능
- ✅ 기존 정의 개선이 필요하면 deprecation 표시 후 신규 정의를 추가

---

## 7. 빠른 시작 — 미국 주식 ETF 데이터로 갈아끼우기 (예시)

가장 흔한 확장 사례. 약 30분.

1. `데이터/` 폴더 교체:
   - `market_data.json` (미국 ETF + 보유종목)
   - `etf_holdings_*.csv` (SPY/QQQ/SOXX/XLK 등)
2. `references/current-dataset.md` 갱신:
   - ETF 목록 표 갱신 (코드: `SPY`, `QQQ`, `SOXX`, `XLK`)
   - 벤치마크 매핑 (`^GSPC`, `^IXIC`, `^SOX`, `^GSPC`)
   - ticker 형식 변환: 미국은 suffix 없음 → 그대로 사용
   - 드롭다운 제외 키워드: `Vanguard`, `iShares`, `SPDR` 등
3. `build_dashboard.py` 실행 → `investment_dashboard.html` 생성
4. 콘솔에서 `[role-map] PATH=fast-path` 확인 (또는 fallback 사유 디버깅)

**Skills.md 본체 파일은 건드릴 필요 없음.** 이게 본 시스템 범용성의 핵심.

---

## Quality Check

- [ ] 새 데이터셋 적용 시 Skills.md 본체 7개 파일은 변경되지 않았는가?
- [ ] 변경된 부분이 `references/current-dataset.md`에 한정되는가?
- [ ] 새 자산군 추가 시 후방 호환성이 유지되었는가? (기존 역할명 보존)
- [ ] 새 뷰가 디자인 일관성 체크리스트를 통과하는가?
- [ ] `[role-map] PATH=fast-path` 또는 `fallback`이 의도대로 출력되는가?
