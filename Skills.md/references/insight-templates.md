---
name: insight-templates
description: >
  Reusable insight message templates for PM/RA banners and RA bottom panels.
  Loaded on-demand by 6-skills-report.md (Step 3) and 5-skills-ra.md (ROW 3).
  Centralized so message wording can be tuned without touching analytical
  rules in 2-skills-criteria.md or 6-skills-report.md.
allowed-tools: Read
---

# 인사이트 메시지 템플릿 — 단일 출처

모든 자동 생성 인사이트의 문장은 본 파일에 집중한다. 트리거 조건은 `2-skills-criteria.md`·`6-skills-report.md`에 있고, 본 파일은 **표시될 메시지 문장**만 정의한다.

문장 안의 `{변수}`는 런타임 치환되는 자리표시자다. 변수 미정의 시 해당 메시지를 출력하지 않는다.

---

## 1. 변수 사전 (Placeholders)

| 변수 | 의미 | 형식 (`design-tokens.md` §6) |
|---|---|---|
| `{etfName}` | ETF 표시명 | 문자열 |
| `{stockName}` | 종목 표시명 | 문자열 |
| `{ticker}` | 종목 코드 | 문자열 |
| `{value}` | 일반 수치 (포맷 미정) | 숫자 |
| `{returnPct}` | 수익률 | 부호 + 소수 2자리 + % |
| `{mddPct}` | MDD | 부호 + 소수 2자리 + % |
| `{weightPct}` | 비중 | 소수 1자리 + % |
| `{gapPct}` | 목표주가 괴리율 | 부호 + 소수 1자리 + % |
| `{excessPct}` | 벤치마크 초과수익 | 부호 + 소수 2자리 + %p |
| `{surprisePct}` | 어닝 서프라이즈 | 부호 + 소수 1자리 + % |
| `{roePct}` | ROE | 소수 1자리 + % |
| `{deRatioPct}` | 부채비율 | 정수 + % |
| `{period}` | 기간 라벨 | "YTD" / "1M" / "3M" / "1Y" |

---

## 2. PM 인사이트 배너 (`6-skills-report.md` Step 3)

우선순위 순으로 평가, 동시 충족 시 최대 3개까지 표시. 조건 미충족 시 폴백 메시지 필수.

| 우선순위 | 트리거 조건 | 색상 토큰 | 메시지 템플릿 |
|---|---|---|---|
| 1 | `MDD < -15%` | `--red` | `리스크 한도 초과 ({mddPct}) — 포지션 축소 검토` |
| 2 | `returns.1m > 50%` | `--gold` | `단기 1M {returnPct} 급등 — 차익실현 검토` |
| 3 | 1위 종목 비중 > 30% | `--gold` | `{stockName} {weightPct} 집중 — 분산 검토` |
| 4 | 초과수익 > +10%p | `--green` | `벤치마크 대비 초과수익 {excessPct}` |
| 5 | 초과수익 < -10%p | `--red` | `벤치마크 대비 하회 {excessPct}` |
| — | 조건 없음 (폴백) | `--green` | `포트폴리오 정상 운용 중` |

---

## 3. RA 인사이트 배너 (`6-skills-report.md` Step 3)

| 우선순위 | 트리거 조건 | 색상 토큰 | 메시지 템플릿 |
|---|---|---|---|
| 1 | 괴리율 ≥ +20% | `--green` | `목표주가 대비 {gapPct} 상승 여력` |
| 2 | 괴리율 ≤ -10% | `--red` | `목표주가 하회 {gapPct} — 하락 리스크` |
| 3 | 최근 분기 매출 서프라이즈 ≥ +5% | `--green` | `최근 분기 매출 컨센서스 {surprisePct} 상회` |
| 4 | 최근 분기 매출 서프라이즈 ≤ -5% | `--red` | `최근 분기 매출 컨센서스 {surprisePct} 하회 — 어닝 쇼크` |
| 5 | PER < 섹터평균 × 0.8 | `--green` | `섹터 평균 대비 PER 저평가` |
| 6 | ROE > 15% | `--green` | `ROE {roePct} — 우수한 자본효율성` |
| 7 | 부채비율 > 200% (비금융) | `--gold` | `부채비율 {deRatioPct} — 재무 레버리지 주의` |
| — | 조건 없음 (폴백) | `--green` | `밸류에이션 정상 범위` |

---

## 4. RA 종합 인사이트 3패널 (`5-skills-ra.md` ROW 3)

각 패널은 4~5줄, 핵심 수치는 `<strong>` 굵게. 데이터 부족 시 패널은 유지하되 "데이터 부족"만 표시.

### 4.1 밸류에이션 패널

| 상태 | 트리거 조합 | 색상 | 메시지 템플릿 |
|---|---|---|---|
| 매수 | 괴리율 ≥ +20% AND PER < 섹터평균 × 0.8 | `--green` | `PER <strong>{per}x</strong>로 섹터 평균 대비 <strong>{perDelta}</strong> 저평가 구간. 목표주가 대비 괴리율 <strong>{gapPct}</strong> — <strong>매수 신호 유효</strong>` |
| 매도 | 괴리율 ≤ -10% AND PER > 섹터평균 × 1.2 | `--red` | `PER <strong>{per}x</strong>로 섹터 평균 대비 <strong>{perDelta}</strong> 고평가 구간. 목표주가 대비 괴리율 <strong>{gapPct}</strong> — <strong>매도 신호</strong>` |
| 중립 | 그 외 | `--gray` | `PER <strong>{per}x</strong>로 섹터 평균 대비 <strong>{perDelta}</strong> 구간. 목표주가 대비 괴리율 <strong>{gapPct}</strong> — 중립` |
| 데이터 부족 | per 또는 sectorAvgPER null | `--gray` | `데이터 부족` |

### 4.2 실적 모멘텀 패널

| 상태 | 트리거 | 색상 | 메시지 템플릿 |
|---|---|---|---|
| 강세 | 매출 서프라이즈 ≥ +5% | `--green` | `최근 분기 매출 서프라이즈 <strong>{surprisePct}</strong>. 매출 추세 <strong>{revYoYPct}</strong>. <strong>어닝 모멘텀 강세</strong>` |
| 둔화 | 매출 서프라이즈 ≤ -5% | `--red` | `최근 분기 매출 서프라이즈 <strong>{surprisePct}</strong>. 매출 추세 <strong>{revYoYPct}</strong>. <strong>어닝 둔화 — 보수적 접근</strong>` |
| 중립 | 그 외 | `--teal` | `최근 분기 매출 서프라이즈 <strong>{surprisePct}</strong>. 매출 추세 <strong>{revYoYPct}</strong>. 중립적 흐름` |
| 데이터 부족 | `consensus_data` 없음 | `--teal` | `컨센서스 데이터 없음 — 모멘텀 평가 불가` |

### 4.3 리스크 패널

| 상태 | 트리거 | 색상 | 메시지 템플릿 |
|---|---|---|---|
| 위험 | 부채비율 > 400% (비금융) | `--red` | `부채비율 <strong>{deRatioPct}</strong> — 재무 위험 구간. 모니터링 필수` |
| 주의 | 부채비율 > 200% (비금융) | `--gold` | `부채비율 <strong>{deRatioPct}</strong> — 레버리지 주의` |
| 금융업 | `is_financial: true` | `--gold` | `금융업 — 부채비율 적용 제외. 자본적정성 별도 검토 필요` |
| 정상 | 그 외 | `--gold` | `부채비율 <strong>{deRatioPct}</strong> — 정상 범위` |
| 데이터 부족 | `debt_to_equity` null | `--gold` | `재무 레버리지 데이터 없음` |

---

## 5. PM 리밸런싱 신호 메시지 (`4-skills-pm.md` Step 3)

### 5.1 패시브 ETF (sector_targets 기반)

| 조건 | 색상 | 메시지 템플릿 |
|---|---|---|
| 현재 - 목표 > +threshold | `--red` | `{sector} {currentPct} / 목표 {targetPct} → 축소 검토` |
| 현재 - 목표 < -threshold | `--gold` | `{sector} {currentPct} / 목표 {targetPct} → 확대 검토` |
| 범위 내 | `--green` | `{sector} {currentPct} / 목표 {targetPct} — 정상` |

### 5.2 패시브 ETF Fallback (sector_targets 없음)

| 조건 | 색상 | 메시지 |
|---|---|---|
| 1위 종목 > 30% | `--gold` | `{stockName} {weightPct} 집중 — 분산 검토` |
| MDD < -15% | `--red` | `리스크 한도 초과 — 포지션 축소 검토` |
| returns.1m > 50% | `--gold` | `단기 {returnPct} 급등 — 차익실현 검토` |
| 조건 없음 | `--green` | `현재 포트폴리오 정상 범위` |

### 5.3 테마형 ETF 집중도

| 조건 | 색상 | 메시지 |
|---|---|---|
| Top1 > 30% | `--gold` | `Top1 종목 비중 {weightPct} (집중 위험)` |
| Top3 합 > 50% | `--gold` | `Top3 종목 비중 합 {weightPct}` |
| Top5 합 > 70% | `--red` | `Top5 종목 비중 합 {weightPct} (과도한 집중)` |
| 모두 정상 | `--green` | `집중도 리스크 정상 범위` |

기여도 표시 형식: `{stockName} {contributionPct}p`

---

## 6. 디자인 원칙

| 원칙 | 의미 |
|---|---|
| **간결성** | 한 줄 메시지 (배너 기준 60자 이내, 패널 기준 4~5줄) |
| **수치 명시** | 모호한 표현 ("높다", "낮다") 대신 실제 값 포함 |
| **행동 가능성** | 가능하면 다음 액션 암시 ("축소 검토", "차익실현 검토") |
| **부정 확정 금지** | "위험" 단정 대신 "검토", "주의", "모니터링" 등 보수적 톤 |
| **다국어 대응 포인트** | 본 파일을 다국어 버전으로 분기하면 메시지만 교체 가능 (`insight-templates-en.md` 등) |

---

## 7. 변경 시 영향 범위

본 파일을 수정하면:
- ✅ Skills 다른 파일은 그대로 (트리거 조건은 그쪽에 있음)
- ✅ 대시보드 코드도 그대로 (변수 자리표시자만 동일하게 유지)
- ⚠️ 메시지 의미를 바꾸지 않을 것 — 임계값과 메시지가 어긋나면 사용자 혼란

---

## Quality Check

- [ ] 모든 트리거 조건이 본 파일의 메시지와 1:1 대응되는가?
- [ ] PM/RA 배너에 폴백(조건 없음) 메시지가 정의되어 있는가?
- [ ] 데이터 부족 케이스가 모든 패널에 명시되어 있는가?
- [ ] 변수 자리표시자가 §1 사전과 일치하는가?
