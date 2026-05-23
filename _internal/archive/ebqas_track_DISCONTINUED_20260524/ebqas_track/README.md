# EB-QAS 별도 트랙 — 진입 anchor (README)

> **본 디렉토리는 메인 트랙과 격리된 후속 연구 트랙의 작업 공간이다.** 메인 트랙(v14 4-way 측정 · 5/26 23:59 LearnUs 발표 deck · 5/27·29 발표 · 5/28 12:00 포스터 · 6/11 최종 보고서)과 분리되어 운영되며, 6/11 최종 보고서 마감 이후 또는 향후 연구 트랙 후보로 활성화된다.

작성: 2026-05-23 22:28 KST. 작성 trigger = 2026-05-23 21:54 KST 강재현 팀원 카카오톡 발화로 진입한 EB-QAS(Empirical-Bayesian Q-error-aware Adaptive Sampling) 트랙의 인프라화 결정(사용자 22:12 KST “v14 aggregate는 당분간 멈춰놓을게, EB-QAS는 다음 세션으로 이어가자”).

## 1. 트랙 진입 anchor (한 줄)

본 트랙의 정본 anchor는 `submission/_drafts/속도는벡터_EBQAS_제안서_확인실험구체화_20260523_215452.md` 한 문서다. EB-QAS의 framing·수식·실험 설계·외부 인용·환각 회피 룰은 모두 그 정본 한 장에서 정의되며, 본 디렉토리 산하 모든 산출물은 그 정본을 출발점·진위 기준으로 삼는다.

## 2. EB-QAS 한 줄 요약

데이터 분포를 미리 안다고 가정하지 않고, 이전 유사 query/predicate의 true cardinality·Q-error를 query-group별 Beta prior `(α_g, β_g)`로 누적해 현재 query sample `s/n`과 결합한 posterior mean `(α_g+s)/(α_g+β_g+n)`으로 cardinality를 추정한다. posterior Q-risk `Q_post = max(p̂/L, U/p̂)`가 충분히 작으면 현재 query에서 sampling을 조기 종료하며, κ cap·decay·mismatch reset으로 잘못된 prior를 안전하게 처리한다. 본 방법은 Exqutor §V-B의 distribution-unaware Bernoulli Adaptive Sampling을 **대체**한다(평균 X · 대체).

## 3. 5/23 본 연구 오프라인 실험 정당성 감사 평결과의 호환성

본 트랙은 2026-05-23 03:14 KST 작성된 본 연구 오프라인 실험 정당성 감사 평결(`_internal/state/오프라인실험_정당성감사_평결_20260523_031402.md`) 위에 선다. 그 평결은 v13 3-way matched 1508 paired의 CaseB 89.1% Q-error 우위가 “분포 인지”의 효과가 아니라 두 독립 추정량 산술평균의 앙상블(분산·zero-hit 감소) 효과임을 통제군 CaseB′(Bernoulli+Bernoulli)/2 1.459 ≤ CaseB 1.477로 입증하고, hyperloglog 무작위 해시조차 CaseA 단독은 +2.57% 악화이나 CaseB(평균)는 median Δ% −4.58%로 둔갑함을 결정적 증거로 제시했다. 또한 distribution-aware 층화로 Bernoulli를 완전 대체(CaseA)하는 것은 portfolio 전체로 악화(better 35.2%·평균 Δ% +12.90%)이며, 엔진 적용 검증 56 cell 범위에서 B1→CaseB latency 무개선(paired Δ% +0.13%·within-cell r=−0.007)임을 확인했다.

본 EB-QAS는 그 평결과 4축 정확 호환된다.

| 5/23 감사 평결 | 본 EB-QAS 방향 | 정합성 |
|---|---|---|
| CaseB 89.1% Q-error 우위 = 두 독립 추정량 산술평균의 앙상블 효과 | CaseB식 평균을 채택 X — B1 자체를 posterior mean으로 대체 | 호환 |
| Distribution-aware 층화로 Bernoulli 완전 대체(CaseA)는 portfolio 악화 | 데이터 분포를 미리 안다고 가정하지 않음 — 정본 §2 제약 1·2·3 명시 | 호환 |
| 엔진 적용 검증 56 cell B1→CaseB latency 무개선 | latency를 objective로 삼지 않고 평가 지표·plan-sensitive subset 한정(정본 §13.2·§D.4·§21 H4) | 호환 |
| method 구현 무결성 결함(skilling_hilbert 가짜·kmeans_neyman·lavallee_hidiroglou Neyman 미적용·신호 5종 PCA/ICA 환원) | method library 의존 X — posterior는 prior mean과 sample proportion 가중평균 한 줄로 산출 | 호환 |

## 4. 메인 트랙 격리 선언

본 트랙은 메인 트랙의 발표·재프레이밍·보고서·포스터·v14 측정과 분리된다. 본 디렉토리 산하 산출물은 메인 트랙 발표 deck·포스터·보고서·재프레이밍 제안서 어느 곳에도 직접 인용되지 않으며, 메인 트랙 음성·방법론적 결과의 정직성을 본 EB-QAS의 “전망”으로 흐리지 않는다. 본 트랙의 활성화·팀 공유·메일·카톡 발신은 사용자 명시 결정 시점에만 진행한다.

본 트랙이 메인 트랙에 영향을 주지 않는다는 보장 4항목:
- 메인 트랙 측정 스크립트(`_internal/scripts/measure_paper_exact.py`)·v14 산출물(`_internal/cache/rq3/v14_summary.md`·`aggregated_v14.parquet`·`paper_exact_v14_20260523/`)·발표 deck 패치본·보고서 신본(`submission/_drafts/속도는벡터_6_11_최종보고서_20260523_215000.md`)에 본 트랙은 patch X.
- 본 트랙 산출물은 `_internal/state/ebqas_track/` 산하 또는 `_internal/handoff/active/handoff_*_EBQAS_*.md` 한정. 메인 트랙 디렉토리(`submission/_drafts/`·`experiments/`·`reference/`)에는 본 트랙 산출물을 직접 작성 X.
- 본 트랙 commit은 메인 트랙 미커밋·신규와 분리(이전 EB-QAS commit `d6d1b5a7` 패턴 유지).
- 본 트랙 산출물은 `v13/v14/ver/wave/phase` 단어를 파일명 분기자로 쓰지 않고 `<문서명>_YYYYMMDD_HHMMSS.ext` 타임코드로 일관.

## 5. 하위 디렉토리 구조

- `실험_spec/` — 정본 anchor §15~17(실험 A~E + hyperparam grid + 구현 의사코드)을 한국어 학술 산문으로 정제한 spec 문서 격납. 본 README와 함께 측정 실행 시 직접 참조하는 작업 spec의 본진.
- `codex_검증/` — Codex 적대 검증(`/codex review --uncommitted` 또는 `codex exec --sandbox read-only` xhigh) 디스패치 spec과 결과 격납. 정본 anchor의 수학적 정확성·안전장치 충분성·paired 비교 통제·leakage 방지·5/23 평결 호환성·외부 인용 verbatim 정확성을 6 축으로 외부 검증.
- `exqutor_대조/` — 정본 anchor가 인용한 arXiv:2512.09695v4와 Capstone CLAUDE.md 정본 v2의 §V-B(adaptive sampling) hyperparam·verbatim 인용 차이를 PDF 직접 추출로 대조한 보고서. 차이 발견 시 정본 anchor inline 수정 권고만(본 README 트랙 외부의 정본 anchor 자체 수정은 별도 결정 후).
- `handoff/` — (선택) 본 EB-QAS 트랙 내부 단계별 보조 handoff 격납. 메인 `_internal/handoff/active/`와 별개로 트랙 내부 사이클 carry 시 사용. 본 README 작성 시점에는 미사용 — 다음 EB-QAS 세션 진입 anchor는 메인 `_internal/handoff/active/`에 둔다.

## 6. 메모리 cross-reference

본 트랙 관련 메모리 anchor는 다음 셋이다.

- `~/.claude/projects/-Users-hyunbin-Capstone/memory/project_ebqas_track.md` — 본 트랙 정본 anchor 메모리. 6/11 이후 활성화 default·환각 회피 룰·다음 세션 carry 4항목.
- `~/.claude/projects/-Users-hyunbin-Capstone/memory/project_offline_audit_20260523.md` — 5/23 감사 평결 carry 메모리. 본 트랙은 그 평결과 4축 호환됨을 명시.
- `~/.claude/projects/-Users-hyunbin-Capstone/memory/MEMORY.md` — 인덱스(Core 섹션에 본 트랙 한 줄).

## 7. 다음 세션 진입 순서

본 디렉토리 작업을 이어 받는 다음 세션은 아래 순서로 read·실행한다.

1. 본 README 정독(트랙 위상·메인 트랙 격리·평결 호환성).
2. 정본 anchor `submission/_drafts/속도는벡터_EBQAS_제안서_확인실험구체화_20260523_215452.md` 정독(framing·수식·실험 A~E·의사코드·외부 인용).
3. `_internal/state/오프라인실험_정당성감사_평결_20260523_031402.md` 정독(5/23 감사 평결 4축).
4. 본 디렉토리 산하 `실험_spec/`·`codex_검증/`·`exqutor_대조/` 신규 산출물 정독.
5. 메모리 3축(`project_ebqas_track.md`·`project_offline_audit_20260523.md`·`MEMORY.md`) 정독.
6. 최신 EB-QAS handoff(`_internal/handoff/active/handoff_*_EBQAS_*.md`) 정독.

## 8. 환각 회피 룰 (carry)

- v13 정본 수치(89.1% / −4.38% / 1344 / 1508 / 35.2% / 12.90% / 1.477 / 1.459 / 1.944 / 1.984 / hyperloglog −4.58% / 56 cell +0.13% / r=−0.007)는 진짜다 — 그러나 인과 귀속(“분포 인지 효과”)은 5/23 감사로 폐기됐다. 본 트랙은 그 인과를 재주장하지 않으며, CaseB식 산술평균을 채택하지 않고 B1 자체를 대체한다는 점으로 평결과 호환된다.
- EB-QAS는 본 디렉토리 작성 시점에 **검증 가설**이다. “EB-QAS가 B1보다 낫다”는 단언 금지(측정 전). 가설 H1~H5(정본 §21)는 측정 결과로만 평가한다.
- 잘못된 group key·κ 과대·prior drift 위험은 정본 §C(stress)·§E(ablation)·§21 H5에 명시 — 활성화 시 발표·보고서에 함께 보고한다.
- Exqutor 본 논문 버전 차이(정본 anchor v4 인용 ↔ Capstone CLAUDE.md 정본 v2)는 `exqutor_대조/` 보고서에서 해결하며, 본 README는 양 버전 공존을 인지 상태로 운영한다.
- 본 EB-QAS를 메인 트랙 발표·재프레이밍·보고서·포스터에 끼워 넣지 않는다.
- 외부 인용(Exqutor·BayesCard·Fauce·Flow-Loss·CardEst PVLDB vol15·Bayes Rules! Beta-Binomial·Efron empirical Bayes·Kuchibhotla 2021 PMLR v139 confidence sequence)의 verbatim·연도·저자·핵심 claim 정확성은 `codex_검증/` Codex 적대 검증으로 외부 fetch 확인한다.
- 발표물(평문)에서 본 트랙의 코드명(EB-QAS·CS-EBQAS·κ·α·β 등) 노출 시 별도 정책 — 활성화 결정 후 사용자 명시 지시로 진행.
- 타임코드 네이밍: 본 디렉토리 산하 모든 산출물 `<문서명>_YYYYMMDD_HHMMSS.ext`. `v13/v14/ver/wave/phase` 단어를 파일명 분기자로 쓰지 않는다.

## 9. 활성화 시기 (carry · 사용자 판단 영역)

- **Default**: 2026-06-11 최종 보고서 마감 이후 또는 향후 연구 트랙 후보 시점.
- **6/11 이전 활성화**: 사용자 명시 결정 시. 활성화 시 박세은(팀장)·강재현(원안 제안)·박광현(지도교수)·박성원(멘토) 공유 시기는 활성화 결정 후 별도 의사결정.
- 본 README는 활성화 시기·공유 시점을 “보류” 상태로 운영한다.
