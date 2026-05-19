# Capstone — 속도는벡터

연세대학교 2026-1학기 인공지능 종합설계 (캡스톤 디자인)

> **현 단계 (2026-05-19)**: 측정 완료 (v13 — 3-way matched 1508 측정). 6/11 최종보고서 초안 작성 완료, 5/27 최종 발표·5/28 전시회 준비 단계.

---

## 📌 팀원 진입 가이드 — "어디부터 봐야 하나요?"

| 우선순위 | 위치 | 무엇 |
|---|---|---|
| ⭐ 1 | `CLAUDE.md` | 프로젝트 컨텍스트·일정·디렉토리 단일 진입점 |
| ⭐ 2 | `submission/_drafts/속도는벡터_6_11_최종보고서_20260519_135021.{md,pdf}` | 6/11 최종보고서 정본 (7장, figure 11) |
| ⭐ 3 | `submission/_drafts/속도는벡터_최종발표_슬라이드.{pptx,pdf}` | 5/27 최종 발표 deck |
| ⭐ 4 | `submission/_drafts/속도는벡터_본연구_narrative_20260518_175437.md` | 본 연구 narrative (발표·보고서 공통 base) |
| ⭐ 5 | `experiments/results/README.md` | 측정 데이터 사전 (변인·결과 구조, 외부 공개용) |
| 6 | `experiments/figures/보고서_6_11/` | 6/11 보고서 figure |
| 7 | `reference/` | 원논문 PDF 69편 + 논문별 총정리 82편 + 심층분석 |

`templates/`(학교 양식)·`_internal/`(조현빈 개인 작업)은 필요할 때만 들어가면 된다.

---

## 🎯 연구 주제

본 연구는 Exqutor 논문(arXiv:2512.09695v2) §V-B Adaptive Sampling 의 **표본 선택(sample selection) 단계 하나**의 개입 — 무작위 Bernoulli 표본 → 분포 인지 stratified 표본 — 이 카디널리티 추정 오차(Q-error)에 미치는 효과를, 전 데이터셋·전 조작 변인에 걸쳐 검증한 완전 실험이다. 카디널리티 추정 알고리즘·논문 식 1-6·표본 예산 N=385 는 그대로 둔다(minimal augmentation).

측정은 **3-way matched** — 한 측정이 세 방식을 동일 조건에서 동시 산출한다.

- **B1** — 대조군. 논문 그대로의 무작위 Bernoulli Adaptive Sampling.
- **CaseA** — 완전 대체. 논문 표본을 우리 method 표본으로 통째 치환 (음성 대조군).
- **CaseB** — 결합. `est_final = (est_B1 + est_method) / 2` 산술 평균.

### 핵심 결과 (v13 — 3-way matched 1508 측정)

- **결합(CaseB) vs 대조군(B1)**: 추정오차 개선 측정 **89.1%** (1344/1508) · 중앙값 Δ% **−4.38%**.
- **완전 대체(CaseA) vs B1**: better 35.2% (negative control — 대체는 불안정, 개선의 원천이 '결합'임을 역으로 입증).
- 측정 method 16종 중 강한 **13** (클러스터링 계열 3 제외).

상세 수치·분석: `experiments/results/raw/REPORT_분석/REPORT_paper_exact_v13.md`.

---

## 👥 팀

| 이름 | 역할 | GitHub |
|------|------|--------|
| 박세은 (팀장) | 일정·문서 관리, 자문 컨택, 회의 주재 | [@triangle-park](https://github.com/triangle-park) |
| 강재현 | 발표 자료 작성·발표 담당, 시각화 | [@newagency](https://github.com/newagency) |
| 조현빈 | Exqutor 코드 분석·실험 구현·통계 분석 | [@johyunbin](https://github.com/johyunbin) |
| 이동욱 | 보고서 작성, 실험 검증, 자문 회신 정리 | [@dlee004](https://github.com/dlee004) |

**지도교수** 박광현 교수님 (BDAI 연구실) · **지도연구원** 임채림 석사 · **멘토** 박성원 (삼성전자 AI센터)

---

## 📅 일정

| 마감 | 제출물 | 상태 |
|------|--------|------|
| 4/28 | 중간보고서 + 중간발표 PDF (LearnUs) | ✅ |
| 4/30 | 중간발표 | ✅ |
| 5/15 | 박광현 교수님 미팅 | ✅ |
| **5/27** | **최종 발표** (10분 발표 + 5분 질의응답) | ⬜ |
| 5/28 | 전시회 자료 (포스터 + 소개 동영상) | ⬜ |
| **6/11** | **최종 보고서** (LearnUs + 홈페이지 게시) | ⬜ |

---

## 🗂 디렉토리 구조 (2026-05-19 총 정리)

```
Capstone/
├── README.md          이 파일 (팀원 진입점)
├── CLAUDE.md          Claude Code 컨텍스트 (자동 로드)
│
├── submission/        ⭐ 우리 팀의 모든 공식 문서
│   ├── _drafts/       팀 공유 작업본 (보고서·발표 deck·포스터·소개영상·표지/요약본·자문메일)
│   │   └── archive/   이전 버전 보존
│   └── 제출완료/       외부 발송 완료 자료 (학교 공식 + 멘토 자문)
│
├── experiments/       ⭐ 실험
│   ├── results/       측정 데이터 (01~06 트랙 + raw 원천 + 데이터 사전 README)
│   ├── figures/       figure (보고서_6_11 · paper_exact_v13)
│   ├── code/          실험 코드 (초기 sprint archive — 측정 도구는 _internal/scripts/)
│   └── config/        실험 파라미터
│
├── plans/             연구 설계·발표 storyline·보고서 outline
├── reference/         원논문 69편 + 총정리 82편 + 심층분석
├── templates/         캡스톤 학교 양식 샘플
│
└── _internal/         ⛔ 조현빈 개인 작업 (팀원 무시 OK)
```

각 디렉토리 상세는 그 안의 `README.md` 참조.

---

## 🛠 자주 쓰는 명령

```bash
# 동기화 (Mac mini ↔ MacBook)
git pull --no-rebase origin main
git add . && git commit -m "..." && git push origin main

# 마크다운 → PDF (Chrome CDP 기반, 한글 폰트 임베드)
python3 _internal/scripts/md2pdf.py <file.md>
```

---

## 🔗 참고

- [Exqutor 논문 (arXiv:2512.09695v2)](https://arxiv.org/abs/2512.09695v2)
- [Exqutor GitHub (BDAI-Research)](https://github.com/BDAI-Research/Exqutor)
- [캡스톤 사이트](https://capstone.cs.yonsei.ac.kr/capstone/)
- [팀 Notion HQ](https://www.notion.so/8110e4b8d680833a90bf01032872b1eb)

---

갱신: 2026-05-19 (디렉토리 총 정리 + v13 측정 결과 반영). 이전 README 는 git history 보존.
