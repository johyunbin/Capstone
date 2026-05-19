# handoff 20260519 14:05 — 6/11 최종 보고서 추가 review pass 완료 (Ch.1~7 정본 갱신)

> 이전 handoff(`_internal/handoff/archive/handoff_20260519_132028_보고서Ch4-7완결.md`) → 본 문서. 이 문서 하나만 읽으면 0% loss 인계 — self-contained.
>
> **핵심 한 줄**: 6/11 최종 보고서 Ch.1~7 완결 초안에 추가 review pass를 적용했다 — 3축 병렬 진단(논리·서사·구조 / 표현·문장 / 수치·figure 정합) → 29건 선별 수정 → 새 컨텍스트 검증(5축 PASS·치명 0건·제출 적합). 보고서 정본이 신규 타임코드 **`135021`**로 갱신됐다. 구조·figure·핵심 수치는 불변, 표현·논리·정합만 다듬었다. **다음 보고서 작업 = 6/10 변환 sprint(md→PDF/docx + 학교 표지 + 소종 요약본)**(§4). 그 전 일정 5/27 발표·5/28 포스터·엔진 검증은 보류·팀 작업 유지(§6).

---

## 0. 가장 먼저 — 정본 문서

- **★ 6/11 보고서 (Ch.1~7 — review pass 반영 정본)**: `submission/_drafts/속도는벡터_6_11_최종보고서_20260519_135021.md` (453줄·7장·figure 11종 임베드)
- 직전 draft (review pass 전, 이력): `submission/_drafts/속도는벡터_6_11_최종보고서_20260519_131514.md`
- review pass 계획: `~/.claude/plans/idempotent-juggling-sketch.md` (완료)
- 보고서 figure 11종: `experiments/figures/보고서_6_11/` (+ fig4_4b 여분 1) · 생성 스크립트 `_internal/scripts/build_report_figures_20260519.py`
- 아웃라인 (7장 spec): `plans/6_11_보고서/6_11_보고서_outline_20260519_122358.md`
- 내용 정본 narrative v8: `submission/_drafts/속도는벡터_본연구_narrative_20260518_175437.md`
- 수치 정본: `_internal/cache/rq3/v13_summary.md` (1508건 3-way 측정)

## 1. 본 연구 framing (불변 — 가장 먼저 내재화)

본 연구는 Exqutor 논문(arXiv:2512.09695v2) §V-B Adaptive Sampling 재현이 아니다. 카디널리티 추정 파이프라인에서 **표본 선택(sample selection) 단계 하나**의 개입(무작위 Bernoulli random sampling → 분포 인지 stratification)이 추정 오차(Q-error)에 미치는 영향을, 전 데이터셋·전 조작 변인에 걸쳐 검증한 완전 실험이다. 측정은 **3-way matched** — B1(대조군, 논문 그대로)·CaseA(완전 대체, 음성 대조군)·CaseB(결합, est_final=(est_b1+est_method)/2.0 산술 평균). 논문 식 1-6·ECQO·카디널리티 추정 알고리즘은 변경 없음(minimal augmentation).

★ 보고서는 **학술 문서** — 정의 용어 B1/CaseA/CaseB(첫 등장 시 "대조군/완전 대체/결합" 병기)와 수식 1-6을 쓸 수 있다. 단 "분포를 안다/모른다" 이분법·"영역" 필러 토큰은 금지. 강한 method는 **13개**(클러스터링 계열 gmm·minibatch_partial·faiss_ivf 3 제외).

## 2. 이 세션(5/19 13:30~14:10)이 한 일

| 항목 | 상태 | 내용 |
|---|---|---|
| review pass 계획 | ✅ | ultraplanning → ExitPlanMode 승인. 계획 `~/.claude/plans/idempotent-juggling-sketch.md` |
| 3축 병렬 진단 | ✅ | Opus 에이전트 3개 find-only — A 논리·서사·구조·framing / B 표현·문장 품질 / C 수치·figure 정합. C: 핵심 수치 전수 정합 확인, 실수정 필요 1건(4.5절 시드 이슈) |
| 29건 수정 적용 | ✅ | 신규 타임코드 파일 `135021`에 21개 행·29건. **4.5절 시드 이슈 해소**(qe_trim "정상 범위"를 285줄 "1.6~1.7"·287줄 "[1.16,1.66]"로 이중 표기 + v13 실측과 불일치 → 비교 서술로 교체) · 비문·주술 호응·대시 삽입구 6건 · 영어명사 선별 한글화(finding·spread·base·robust·baseline·evidence) · '유의%' 정의 보강 · 전환 다리 2건 · minibatch +14.06% 명확화 |
| 검증 | ✅ | 새 컨텍스트 Opus 에이전트 — 5축(수치 v13 정합·regression·framing·figure·미해결) **전부 PASS, 치명 0건, 제출 적합**. 메인 세션이 diff 직접 확인(453줄 유지·의도한 21행만 변경) |
| REPORT v13 §8 정정 | ✅ | 사용자 요청 — 보조 분석 문서 `REPORT_paper_exact_v13.md` §8 K granularity가 옛 6-cell·n=96 stale 수치. 정본 `paired_delta_v13.parquet` 재계산으로 8-cell·n=128 정정(8건, §8 밖 56·366줄 동일 주장 포함). v13_summary §5 일치 확인 |
| 5/19 일괄 커밋 | ✅ | 마지막 커밋(ae95270) 이후 미커밋이던 5/19 다세션 작업을 한 커밋으로 저장 |

- 구조·figure 11종·핵심 headline 수치는 **불변**. 이번 수정은 표현·논리·정합 다듬기에 한정.

## 3. 핵심 수치 — v13 정본 (`v13_summary.md` — 보고서 전수 대조 기준, 불변)

- 측정 **1508건 3-way matched** (B1·CaseA·CaseB 각 1508, 통합 4524 row).
- **결합(CaseB) vs 대조군(B1)**: better **89.1%**(1344/1508) · 중앙값 Δ% **−4.38%** · 평균 −3.06%(이상치 2건 제외 −4.09%) · 유의 65.3% · 효과크기 large 72.1%.
- **완전 대체(CaseA) vs B1**: better 35.2% · 평균 +12.90% (negative control). CaseB가 CaseA를 **96.5%** 우월.
- selectivity 0.001/0.01/0.10 → better **83.3/87.6/97.5%**. K granularity 8-cell K=10/20/30 → **83.6/89.8/85.9%** (K=20 최강).
- B1 qe_trim K=10/20/30 = **1.5132/1.4402/1.5091** (이전 캠페인 K=10 손상 2.2~3.3 해소 검증).
- method 16종: 강한 **13** / 클러스터링 3 제외. fit_time sparse_rp **2.91s** ~ skilling_hilbert **53.92s**. Type별 측정 수 272·224·464·368·180.

## 4. ★ 다음 세션 task — 6/10 변환 sprint

보고서 본문 Ch.1~7은 **완결 + review pass 반영 완료**. 아웃라인 §9.2 sprint 기준 남은 작업:

1. **팀원 장별 review·확정** (5/29~6/9) — 4인 분담. Claude의 추가 review pass는 본 세션에 완료. 팀 작업.
2. **6/10 변환 sprint** — `submission/_drafts/속도는벡터_6_11_최종보고서_20260519_135021.md`를 md→PDF/docx 변환.
   - PDF는 Chrome CDP만 사용 — 실행: `python3 _internal/scripts/md2pdf.py <file.md>` (**fpdf2 금지** — 한글 깨짐).
   - ★ md2pdf.py 경로는 `_internal/scripts/md2pdf.py`다 — 보고서 머리말·CLAUDE.md가 적은 `scripts/md2pdf.py`와 경로가 다름.
   - figure 임베드는 `../../experiments/figures/보고서_6_11/` 상대경로 — 변환 시 경로 확인.
3. **학교 표지 양식 + 소종 요약본** (6/10) — `templates/`(forms/ + samples/) 학교 양식 참조, 종합설계 결과보고서 표지·요약 form 작성.
4. **6/11 최종 검토 + 제출** — LearnUs 제출 + 캡스톤 홈페이지 게시.

## 5. 산출물 경로

| 산출물 | 경로 | 상태 |
|---|---|---|
| 6/11 보고서 (review pass 정본) | `submission/_drafts/속도는벡터_6_11_최종보고서_20260519_135021.md` | 완결·검증 통과 |
| 직전 draft (review pass 전, 이력) | `submission/_drafts/속도는벡터_6_11_최종보고서_20260519_131514.md` | 이력 — 135021이 정본 |
| review pass 계획 | `~/.claude/plans/idempotent-juggling-sketch.md` | 완료 |
| 보고서 figure 11종 | `experiments/figures/보고서_6_11/` | 완성 |
| figure 생성 스크립트 | `_internal/scripts/build_report_figures_20260519.py` | 완성 |
| 보고서 아웃라인 (7장) | `plans/6_11_보고서/6_11_보고서_outline_20260519_122358.md` | — |
| 본 handoff | `_internal/handoff/active/handoff_20260519_140541_보고서reviewpass.md` | — |

## 6. 보류·팀 작업 항목 (carry-forward — 변경 없음)

- **5/27 발표 deck** — `submission/_drafts/속도는벡터_최종발표_슬라이드.{pptx,pdf}` 19장, 검증 완료(사용자 제출만).
- **5/28 전시회 포스터 + 소개 동영상 키트** — 제작·검증 완료. 남은 것은 팀 작업(동영상 녹음·MP4·YouTube 업로드 → QR 생성·포스터 삽입 → 5/28 12:00 제출). 정밀 절차는 `archive/handoff_20260519_114233_포스터영상_키트완성.md` §3·§4·§5.
- **엔진 적용 검증** — 보류 유지(취소 아님). 재개 정본 = plan `~/.claude/plans/swift-discovering-engelbart.md` + `archive/handoff_20260519_065400_엔진검증_harness골격.md`. 엔진 결과는 보고서 Ch.5 향후 작업에만 반영됨.

## 7. 정책 메모

- 수치는 v13 정본(`v13_summary.md`)만. 평균·중앙값·이상치 제외 평균 병기.
- 보고서는 학술 문서 → B1/CaseA/CaseB 정의 용어·수식 1-6 사용 OK. "분포 안다/모른다" 이분법·"영역" 필러 금지.
- 비자명 작업은 ultraplanning → ExitPlanMode 승인 → 실행.
- 커밋·push·동기화는 사용자 명시 요청 시만. 본 세션 산출물 미커밋.

## 8. 미해결 / 사용자 복귀 확인

- **5/19 미커밋 작업 전체를 일괄 1커밋으로 저장 완료** ("세션 5/19 — 미커밋 작업 일괄 저장" — 6/11 보고서 파이프라인·5/27 deck·5/28 포스터/동영상 키트·엔진검증 scripts·handoff). push는 미실행 — 명시 요청 시만.
- **REPORT v13 §8 정정 완료**(본 세션) — `experiments/results/raw/REPORT_분석/REPORT_paper_exact_v13.md` §8 K granularity 옛 6-cell·n=96 → 정본 8-cell·n=128. 단 같은 파일 **366줄에 "16 method 중 14개 견고하게 우월" 잔존** — 정본은 강한 method **13**(클러스터링 gmm·minibatch_partial·faiss_ivf 3 제외). §6.1 등에도 "14" 표기가 있을 수 있어 13으로 통일 정정 권장 — K granularity와 무관한 별개 stale.
- `build_report_figures_20260519.py` Pyright 정적 타입 경고 9건 잔존 — 런타임 무해.

## 환각 회피 룰 (필독)

- 수치는 `v13_summary.md` 실측: 89.1%(1344/1508)·중앙값 −4.38%·평균 −3.06%(이상치 제외 −4.09%)·CaseA 35.2%·CaseB가 CaseA 96.5% 우월·selectivity 83.3/87.6/97.5·K(8-cell) 83.6/89.8/85.9·fit_time 2.91~53.92s·Type 272/224/464/368/180.
- B1 qe_trim K별 = **1.5132/1.4402/1.5091** 정본(v13_summary §2). 이전 캠페인 K=10 손상 = **2.2~3.3**. 보고서 4.5절은 review pass에서 옛 "정상 범위 1.6~1.7"·"[1.16,1.66]" 표기를 제거하고 이 실측값으로 정정함 — carry 금지.
- v11/v12-era 표현("280/280 byte-identical"·"Fig 12 1.618"·paired 92.5%) carry 금지. v12 headline 92.2%/−6.25%는 보고서 §4.1 v12→v13 정정 경위에만 등장.
- 보고서 구조 = 학교 7장. figure 11종 = 그림 1-1·2-1·3-1·3-2·3-3·4-1·4-2·4-3·4-4·5-1·6-1. 강한 method 13·클러스터링 3 제외. faiss_ivf = P2.
- review pass 수정 행(28·34·40·54·58·97·101·108·116·148·170·194·200·216·228·257·267·277·285·287·309)은 표현·정합 다듬기 — 수치·구조·figure 불변.

---

작성: 2026-05-19 14:30 KST · 6/11 최종 보고서 Ch.1~7에 추가 review pass(3축 진단·29건 수정·검증 통과) 적용, 정본 `135021` 갱신 + REPORT v13 §8 stale 수치 정정 + 5/19 미커밋 작업 일괄 커밋 → 다음 = 6/10 변환 sprint(PDF/docx·표지·요약본, §4).
