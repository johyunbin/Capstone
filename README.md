# Capstone — 속도는벡터

연세대학교 2026-1학기 인공지능 종합설계 (캡스톤 디자인)

> **현 단계 (5/8 22:00):** W1 sprint 완료 (RQ1+RQ2+RQ3 100%, 4강 도출, multi 25× shrinkage), 자문 메일 v4 (박성원 멘토) ready, Multi 측정 launch 대기.

---

## 📌 팀원 진입 가이드 — "어디부터 봐야 하나요?"

처음 들어왔거나 오래간만에 돌아왔다면 다음 순서로 보면 된다.

| 우선순위 | 위치 | 무엇 |
|---|---|---|
| ⭐ **1순위** | `CLAUDE.md` | 프로젝트 컨텍스트·일정·디렉토리 설명 단일 진입점 (자동 로드). |
| ⭐ **2순위** | `submission/_drafts/속도는벡터_연구지도확인서_20260508_v3.{md,pdf}` | **자문 메일 v4 — 박성원 멘토 송부 준비본**. RQ3 paradigm 확정 + 4강 + Adaptive 비교 narrative. |
| ⭐ **3순위** | `plans/최종보고서_outline_v2_20260508.md` | 6/11 최종보고서 outline (8 section). |
| ⭐ **4순위** | `experiments/` | 모든 실험 코드·데이터·결과·시각화. 폴더 안 `README.md` 에 RQ별·Phase별 정리. |
| 5순위 | `submission/_drafts/속도는벡터 — Academic v3 · Final 5_27.{pdf,pptx}` | 5/27 최종 발표 deck (16 page Academic v3) + `academic_deck_v3_source/academic-deck/Slides.jsx`. |
| 6순위 | `plans/` | 연구 설계안 (v3 → v4 → 재설계안 → RQ3 paradigm 확정안 (5/8)). |
| 7순위 | `reference/` | 원논문 PDF (69편) + 논문별 총정리 (82편) + 심층분석 시리즈. 참고 자료. |

다음 폴더는 **필요할 때만** 들어가면 된다.

| 폴더 | 언제 |
|---|---|
| `templates/` | 캡스톤 학교 양식 PDF 샘플 — 새 보고서 양식 잡을 때 |
| `_internal/` | 조현빈 개인 작업 (자동화 지침·문서 빌드 도구·회의록·handoff). **팀원은 무시해도 됨** |

---

## 🎯 연구 주제

**Skew-Aware Stratified Sampling for Vector-Augmented Analytical Query Optimization**

Exqutor 논문 (arXiv:2512.09695v2) 가 단일 테이블 vector range query 시나리오에서 활성화되지 않는 사각지대를 직접 소스 검증으로 드러내고, 두 단계 sanitize — `TABLESAMPLE SYSTEM → BERNOULLI` 의 한 줄 교체와 data-side k-means K=20 기반 stratified sampling 의 native 구현 — 로 카디널리티 추정 정확도를 정량 개선한다.

### 핵심 결과 (2026-05-08 W1 sprint 종합)

- **RQ1 (Skew → BERN 부정확)**: 13/13 cell ρ < 0 (10 single + 3 multi), DEEP-KM20 ρ = -0.680 [-0.800, -0.440] — selectivity 작을수록 BERN 부정확 단조 증가.
- **RQ2 (분포 known)**: 12 cell × 5 mode × 5 sel → 51/52 paired CI 0 제외, σ-allocation 격차 < 1 % → 어느 mode 든 비슷, 균등도 충분.
- **RQ3 (분포 unknown, 30 method 비교)**: Tier 1 17종 (avg -8.04 ~ -6.83 %, spread 1.21 %p), **4강** ★1 HDBSCAN -8.04 / ★2 MB_partial -7.63 / ★3 Hilbert -7.54 / ★4 Hybrid -7.13.
- **Multi-table 일반화**: 단일 sweet spot 17.13 % → multi 0.67 % (25× shrinkage) → "단일 정확성 = multi 정확성 *필요조건* 만 성립".
- **PDX (SIGMOD 2025) 학술 confirmation**: intrinsic_dim + skewness driven algorithm selection (본 thesis 와 정확 일치).

자세한 narrative 와 실험 표는 `experiments/results/RQ1_RQ2_RQ3_종합_master_v6_draft_filled_partial.{md,pdf}` 참조.

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
**멘토**: 박성원

---

## 📅 일정

| 마감 | 제출물 | 상태 |
|------|--------|------|
| 4/28 (화) | 중간보고서 + 중간발표 PDF (LearnUs) | ✅ |
| 4/30 (목) | 중간발표 (인종 A428, 강재현) | ✅ |
| 5/8 (목) 19:00 | RQ1+RQ2+RQ3 sprint 마감 + 비대면 회의 | ✅ |
| **5/9 ~ 5/15** | **자문 메일 발송 (박성원 멘토 + 임채림 석사 + 교수님) + Adaptive 비교 launch** | ← 현재 |
| 5/22 | 교수님 미팅 | |
| **5/27 (수)** | **★ 최종 발표 (D-19)** | |
| 5/28 | 전시회 자료 마감 | |
| **6/11 (수)** | **★ 최종보고서 제출 (D-34)** | |

---

## 🗂 디렉토리 트리 (전체)

```
Capstone/
├── README.md                              ← 이 파일 (팀원 진입점)
├── CLAUDE.md                              ← Claude Code 컨텍스트 (자동 로드)
│
├── submission/                            ⭐ 우리 팀의 모든 공식 문서 — README 있음
│   ├── _drafts/                           ⭐ 팀과 공유할 최신본 + archive — README 있음
│   │   ├── 속도는벡터_연구지도확인서_20260508_v3.{md,pdf}     ⭐ 자문 메일 v4 (박성원 멘토)
│   │   ├── 속도는벡터_자문메일_박성원멘토_20260508_v4.md      자문 본문 v4
│   │   ├── 속도는벡터 — Academic v3 · Final 5_27.{pdf,pptx}  5/27 최종 발표 deck (16 page)
│   │   ├── academic_deck_v3_source/                       Slides.jsx 원본
│   │   ├── 팀원_요약_20260508.pdf                          팀원 진입 요약
│   │   ├── 팀원_슬라이드가이드_20260508.pdf                  발표 가이드
│   │   └── archive/                                       이전 버전 모음
│   └── 제출완료/                          외부에 보낸 자료 (학교 공식 + 멘토 자문)
│
├── experiments/                           ⭐ 실험 — README 있음
│   ├── code/rq1/                          서버 실험 스크립트
│   ├── code/local_analysis/               로컬 분석 스크립트
│   ├── results/                           RQ1·RQ2·RQ3 measurement + master_v6
│   ├── figures/                           시각화
│   └── config/                            실험 파라미터
│
├── plans/                                 연구 설계안 + 최종보고서 outline v2
│   ├── RQ재정립_20260505_2122.md           v6 RQ 재정립 (5/5)
│   ├── 최종보고서_outline_v2_20260508.md   ⭐ 6/11 보고서 8 section outline
│   └── archive/                            v3 (4/3) → v4 (4/15) 이력
├── reference/                              참고 자료 (논문 69편 + 총정리 82편 + 분석)
├── templates/                              캡스톤 학교 양식 샘플 (forms/ + samples/)
│
└── _internal/                             ⛔ 팀원 무시 OK (조현빈 개인 작업)
    ├── handoff_v14_*.md                   ⭐ 다음 세션 진입용 (5/8 22:00 기준)
    ├── records/                           회의록 (kakaotalk + weekly)
    ├── scripts/                           문서 빌드 도구 (md2pdf 등)
    ├── cache/                             실험 측정 캐시
    ├── guideline/                         Claude Code 자동화 지침
    └── audit_*.md / handoff_*.md          5/8 sprint 산출물
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
