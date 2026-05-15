# Capstone — 속도는벡터

연세대학교 2026-1학기 인공지능 종합설계 (캡스톤 디자인)

> **현 단계 (2026-05-16 01:16 KST):** Framing 단순화 단계 진행 중 — **"sample selection 영역만 우리 contribution + paper §V-B Adaptive Eq 1-6 그대로 활용"** (박세은 5/15 20:49 의도 일치). v8 chain stop (50 method 영역 framing 불일치) → **v10 chain launch** (사용 16 method × 12 cell × CaseB ≈ 129 file, Pareto Top 5 ★ + paradigm rep 11). 측정 portfolio 1001 file (B1 9 + CaseA 폐기 + CaseB 996 + 신규 v10) base 위 Exqutor §V-B 재현 100% 유지. 5/27 발표 prompt v11 (3 part) paste 대기 + 5/22 박광현 미팅 자료 준비 단계.

---

## 📌 팀원 진입 가이드 — "어디부터 봐야 하나요?"

처음 들어왔거나 오래간만에 돌아왔다면 다음 순서로 보면 된다.

| 우선순위 | 위치 | 무엇 |
|---|---|---|
| ⭐ **1순위** | `CLAUDE.md` | 프로젝트 컨텍스트·일정·디렉토리 단일 진입점 (자동 로드) |
| ⭐ **2순위** | `submission/_drafts/속도는벡터 — Academic v3 · Final 5_27.{pdf,pptx}` | **5/27 최종 발표 deck** (16 page Academic v3, 5/8 base — 5/27 까지 update 진행) |
| ⭐ **3순위** | `submission/_drafts/속도는벡터_자문메일_박성원멘토_20260509_v5.{md,pdf}` | 박성원 멘토 자문 메일 v5 (5/9 finalize) |
| ⭐ **4순위** | `plans/5_27_storyline_draft_20260511_1410.md` | **5/27 발표 storyline v2** (5/11 정정 4건 반영, paradox finding + 92.9% anchor) |
| ⭐ **5순위** | `plans/최종보고서_outline_v2_20260508.md` | 6/11 최종보고서 outline (8 section, base) |
| 6순위 | `experiments/figures/paper_exact_v7/` | 6 figure (paradigm rollup, Cliff's δ bucket, CaseA vs CaseB, top winners, effect size, narrative diagram) |
| 7순위 | `experiments/` | 모든 실험 코드·데이터·결과 폴더 |
| 8순위 | `reference/` | 원논문 PDF (69편) + 논문별 총정리 (82편) + 심층분석 시리즈 |

다음 폴더는 **필요할 때만** 들어가면 된다.

| 폴더 | 언제 |
|---|---|
| `templates/` | 캡스톤 학교 양식 PDF 샘플 — 새 보고서 양식 잡을 때 |
| `_internal/` | 조현빈 개인 작업 (자동화 지침·문서 빌드 도구·회의록·handoff). **팀원은 무시해도 됨** |

---

## 🎯 연구 주제

**Skew-Aware Stratified Sampling for Vector-Augmented Analytical Query Optimization**

본 연구는 Exqutor 논문 (arXiv:2512.09695v2) 의 §V-B Adaptive Sampling 영역 (인덱스 부재 시 Bernoulli + 모멘텀 기반 동적 sample size) 에 대해 paper 의 모든 hyperparam·query·threshold·trim 정의를 verbatim 으로 재현한다. 이를 baseline 으로 두고 우리의 9 paradigm × 56 method ensemble augment 가 카디널리티 추정 정확도에 가져오는 정량적 가치를 paired Δ% + 효과크기 (Cliff's δ + Hedges' g) 로 검증한다. ECQO §V-A (인덱스 있을 때 HNSW range query 활용) 영역은 paper main result 로 그대로 인정하며, 우리 contribution 은 §V-B 영역 augment 로 한정한다.

### 핵심 결과 (2026-05-11 paper exact 재현 종합)

- **Exqutor 100% 정확 재현**: paper Fig 12 영역 8 cells mean qe_trim **1.6180** (paper 1.69 vs **−4.26%**, paper review-grade)
- **RQ1 (random sampling skew 부정확)**: DEEP/SIFT sf=100 × sel{0.01, 0.10} mean gap +3.74% (Bernoulli vs KM20 stratified)
- **RQ2 (분포 알면 prop allocation 답)**: KM20 5-way Bern→Prop **−9.53%**. Anti 1.540 < Prop 1.580 < Neyman 1.595 paradox 발견 (σ_j range 1.3-1.6× narrow + N_i CV=0 → alloc 변별력 미미)
- **RQ3 (분포 모르면 ensemble augment)**: CaseB Cliff's δ large better **63.5%** (284/447) + Hedges' g large **56.4%** (252) + paired CaseB > CaseA **92.9%** (404/435). Paradigm rollup P10 Density −11.93% / P9 InfoTheoretic −10.22% / P3 Streaming −6.53% / P4 DimReduction −5.92% / P2 Spatial −5.36% (5 paradigm 모두 ensemble 가치 입증)
- **Honest limitation**: 측정 미커버 233 cells (20.5%) 9 카테고리 정직 분류 (algorithm audit drop / 자원 한계 / paper §V-A scope 외 / wrapper timeout 부재 등)

자세한 narrative 와 측정 표는 `experiments/figures/paper_exact_v7/` 6 figure + REPORT v7 (server `/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact/REPORT_paper_exact.md`) 참조.

---

## 👥 팀

| 이름 | 역할 | GitHub |
|------|------|--------|
| 박세은 (팀장) | 일정·문서 관리, 자문 컨택, 회의 주재 | [@triangle-park](https://github.com/triangle-park) |
| 강재현 | 발표 자료 작성·발표 담당, 시각화 | [@newagency](https://github.com/newagency) |
| 조현빈 | Exqutor 코드 분석·실험 구현·통계 분석 | [@johyunbin](https://github.com/johyunbin) |
| 이동욱 | 보고서 작성, 실험 검증, 자문 회신 정리 | [@dlee004](https://github.com/dlee004) |

**지도교수**: 박광현 교수님 (BDAI 연구실)
**지도연구원**: 임채림 석사
**멘토**: 박성원 (삼성전자 AI센터)

---

## 📅 일정

| 마감 | 요일 | 제출물 | 상태 |
|------|---|--------|------|
| 4/28 | 화 | 중간보고서 + 중간발표 PDF (LearnUs) | ✅ |
| 4/30 | 목 | 중간발표 (인종 A428, 강재현) | ✅ |
| 5/8 | 목 | RQ1+RQ2+RQ3 sprint 마감 + 비대면 회의 | ✅ |
| 5/9~5/11 | | paper exact 재현 측정 완료 (898 file) + 11 axis cross-verification | ✅ |
| **5/15 14:00** | **금** | **★ 박광현 교수님 미팅 (D-4)** | ⬜ |
| 5/15~5/20 | | 자문 메일 박성원 멘토 발송 + 회신 대기 | ⬜ |
| ~5/21 | | 발표 자료 초안 마감 | ⬜ |
| 5/26 | | 발표 자료 최종 마감 | ⬜ |
| **5/27** | **수** | **★ 최종 발표 (D-16)** | ⬜ |
| 5/28 | | 전시회 자료 마감 | ⬜ |
| 6/5 | | 전시회 | ⬜ |
| **6/11** | **목** | **★ 최종 보고서 (D-31)** | ⬜ |

---

## 🗂 디렉토리 트리

```
Capstone/
├── README.md                              ← 이 파일 (팀원 진입점)
├── CLAUDE.md                              ← Claude Code 컨텍스트 (자동 로드)
│
├── submission/                            ⭐ 우리 팀의 모든 공식 문서
│   ├── _drafts/                           팀 공유 최신본
│   │   ├── 속도는벡터 — Academic v3 · Final 5_27.{pdf,pptx}  5/27 발표 deck (16 page Academic v3 base)
│   │   ├── 속도는벡터_연구지도확인서_20260508_v3.{md,pdf}     자문 메일 v5 base
│   │   ├── 속도는벡터_자문메일_박성원멘토_20260509_v5.{md,pdf} ⭐ 박성원 멘토 자문 메일 v5
│   │   ├── 팀원_요약_20260509.pdf                          팀원 진입 요약
│   │   ├── 팀원_슬라이드가이드_20260509.pdf                  발표 가이드
│   │   ├── 팀원_이해용_종합_20260509.pdf                     팀원 종합 자료
│   │   └── archive/                                       이전 버전 모음 (한글 폴더 12종, 5/11 정리)
│   └── 제출완료/                          외부에 보낸 자료 (학교 공식 + 멘토 자문)
│
├── experiments/                           ⭐ 실험
│   ├── code/                              실험 스크립트
│   ├── results/                           RQ1·RQ2·RQ3 measurement
│   ├── figures/                           시각화
│   │   └── paper_exact_v7/                ⭐ 6 figure (5/11 신규, paradigm rollup + Cliff's δ + violin + winners + scatter + narrative)
│   └── config/                            실험 파라미터
│
├── plans/                                 연구 설계 + storyline + outline
│   ├── 5_27_storyline_draft_20260511_1410.md  ⭐ 5/27 발표 storyline v2 (5/11 정정)
│   ├── 최종보고서_outline_v2_20260508.md       ⭐ 6/11 보고서 8 section outline
│   └── archive/                            이전 RQ 재정립 + 회의 outline
├── reference/                              참고 자료 (논문 69편 + 총정리 82편)
├── templates/                              캡스톤 학교 양식 샘플
│
└── _internal/                             ⛔ 팀원 무시 OK (조현빈 개인 작업)
    ├── handoff/active/handoff_v8_session_total_cleanup_20260511_1734.md  ⭐ 새 세션 인계 anchor (0% loss)
    ├── MASTER_README.md / MASTER_HANDOFF.md / METHOD_REGISTRY.md / EXPERIMENT_REGISTRY.md / SERVER_REGISTRY.md
    ├── state/_schedule.md                 핵심 일정
    ├── records/                           회의록 (kakaotalk + weekly)
    ├── scripts/                           문서 빌드 도구 (md2pdf 등) + 측정 script
    ├── cache/, guideline/, learning/      자동화 지침 + 학습 자료
    ├── method_audit/                      method 검증 (8 agent audit, 11 file)
    ├── validation/                        4-layer audit
    └── 문서_archive/                       이전 handoff + 5/8 시점 outdated docs (5/11 정리)
```

---

## 🛠 자주 쓰는 명령

```bash
# 동기화 (Mac mini ↔ MacBook)
git pull --no-rebase origin main
git add . && git commit -m "sync: ..." && git push origin main

# 마크다운 → PDF (조현빈 개인 도구, Chrome CDP 기반)
python3 _internal/scripts/md2pdf.py <file.md>
```

---

## 🔗 참고

- [Exqutor 논문 (arXiv:2512.09695v2)](https://arxiv.org/abs/2512.09695v2)
- [Exqutor GitHub (BDAI-Research)](https://github.com/BDAI-Research/Exqutor)
- [캡스톤 사이트](https://capstone.cs.yonsei.ac.kr/capstone/)
- [팀 Notion HQ](https://www.notion.so/8110e4b8d680833a90bf01032872b1eb)
