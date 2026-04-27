# Capstone — 속도는벡터

연세대학교 2026-1학기 인공지능 종합설계 (캡스톤 디자인)

---

## 📌 팀원 진입 가이드 — "어디부터 봐야 하나요?"

처음 들어왔거나 오래간만에 돌아왔다면 다음 순서로 보면 된다.

| 우선순위 | 위치 | 무엇 |
|---|---|---|
| ⭐ **1순위** | `submission/_drafts/` | 작업 중인 보고서·발표자료·온보딩 자료가 모두 여기 있다. 폴더 안 `README.md` 가 단일 진입점. **마감 임박 자료**도 여기. |
| ⭐ **2순위** | `experiments/` | 모든 실험 코드·데이터·결과·시각화. 폴더 안 `README.md` 에 RQ별·Phase별 정리. |
| 4순위 | `plans/` | 연구 설계안 (v3 → v4 → 재설계안 → RQ3 7-way 설계). 가장 최근의 RQ3 설계는 `plans/RQ3설계안_*.md`. |
| 5순위 | `reference/` | 원논문 PDF (69편) + 논문별 총정리 (82편) + 심층분석 시리즈. 참고 자료. |

다음 폴더는 **필요할 때만** 들어가면 된다.

| 폴더 | 언제 |
|---|---|
| `templates/` | 캡스톤 학교 양식 PDF 샘플 — 새 보고서 양식 잡을 때 |
| `_internal/` | 조현빈 개인 작업 (자동화 지침·문서 빌드 도구·회의록·주간보고). **팀원은 무시해도 됨** |

---

## 🎯 연구 주제

**Skew-Aware Stratified Sampling for Vector-Augmented Analytical Query Optimization**

Exqutor 논문 (arXiv:2512.09695v2) 가 단일 테이블 vector range query 시나리오에서 활성화되지 않는 사각지대를 직접 소스 검증으로 드러내고, 두 단계 sanitize — `TABLESAMPLE SYSTEM → BERNOULLI` 의 한 줄 교체와 data-side k-means K=20 기반 stratified sampling 의 native 구현 — 로 카디널리티 추정 정확도를 정량 개선한다.

### 핵심 결과 (2026-04-17 기준)

- **단일 테이블 사각지대 발견**: `vector.c` line 243 의 `if (table_count > 2)` hook 조건 → 단일 테이블 쿼리는 PostgreSQL default selectivity (1/3) 로 fall-through. 원논문에 명시되지 않은 design constraint.
- **5-seed 95 % CI 본선 anchor**: DEEP 1M +1.64 % [+1.11, +2.18], DEEP 8M +1.76 % [+0.65, +2.86], SIFT 1.5M +3.07 % [+2.66, +3.48].
- **Two-Level Decomposition**: Level 2 (공간 인식) 단독으로 좁은 selectivity (s=0.010) 영역에서 +19.60 %p 기여 → 본 연구의 핵심 가설인 "쏠림 → 공간 인식 가치 증가" 인과 입증.
- **HHI · CV 정량화**: DEEP CV 0.234 vs SIFT CV 0.394 (68 % 더 쏠림) → KM20 효과의 데이터셋별 격차를 사전 예측.

자세한 narrative 와 실험 표는 `submission/팀원 온보딩_20260417.md` 참조.

---

## 👥 팀

| 이름 | 역할 | GitHub |
|------|------|--------|
| 박세은 (팀장) | 일정·문서 관리, 자문 컨택, 회의 주재 | [@triangle-park](https://github.com/triangle-park) |
| 강재현 | 발표 자료 작성·발표 담당, 시각화 | [@newagency](https://github.com/newagency) |
| 조현빈 | Exqutor 코드 분석·실험 구현·통계 분석 | [@johyunbin](https://github.com/johyunbin) |
| 이동욱 | 보고서 작성, 실험 검증, 자문 회신 정리 | [@dlee004](https://github.com/dlee004) |

**지도교수**: 박광현 교수님 (BDAI 연구실)
**조교**: 이채림 조교
**멘토**: 박성원

---

## 📅 일정

| 마감 | 제출물 | 상태 |
|------|--------|------|
| **4/28 (화)** | **중간발표 + 중간보고서** | ← 다음 마감 |
| 5/27 ~ 5/29 | 최종발표 + 전시회 마감 | |
| 6/5 | 전시회 | |
| **6/11** | **최종보고서** | |

---

## 🗂 디렉토리 트리 (전체)

```
Capstone/
├── README.md                              ← 이 파일 (팀원 진입점)
├── CLAUDE.md                              ← Claude Code 컨텍스트 (자동 로드)
│
├── submission/                            ⭐ 우리 팀의 모든 공식 문서 — README 있음
│   ├── _drafts/                           ⭐ 팀과 공유할 최신본 + archive — README 있음
│   │   ├── 속도는벡터_중간보고서_*.{docx,pdf}     4/27 빌드, 17 페이지
│   │   ├── 속도는벡터_중간발표_*.{docx,pdf,pptx}  4/17 v2 발표자료
│   │   ├── 팀원 온보딩_20260417.{md,pdf}        새 합류 팀원 첫 진입 자료
│   │   └── archive/                            이전 버전 모음
│   └── 제출완료/                          외부에 보낸 자료 (학교 공식 + 멘토 자문)
│
├── experiments/                           ⭐ 실험 — README 있음
│   ├── code/rq1/                          서버 실험 스크립트
│   ├── code/local_analysis/               로컬 분석 스크립트
│   ├── results/rq1_motivation/            parquet · json · 분석 md
│   ├── results/rq2_aware/                 RQ2 본선 결과
│   ├── figures/                           시각화
│   └── config/                            실험 파라미터
│
├── plans/                                 연구 설계안 (RQ3 7-way 등)
├── reference/                              참고 자료 (논문·총정리·분석)
├── templates/                             캡스톤 학교 양식 샘플
│
└── _internal/                             ⛔ 팀원 무시 OK (조현빈 개인 작업)
    ├── records/                           회의록 + 주간보고
    ├── scripts/                           문서 빌드 도구 (md2pdf 등)
    ├── guideline/                         Claude Code 자동화 지침
    ├── learning/                          학습 자료
    └── session_state.json                 세션 상태
```

---

## 🛠 자주 쓰는 명령

```bash
# 동기화 (Mac mini ↔ MacBook)
git pull --no-rebase origin main
git add . && git commit -m "sync: ..." && git push origin main

# 중간보고서 v0 재빌드
python3 _internal/scripts/_build_docx_v0.py

# 마크다운 → PDF (조현빈 개인 도구)
python3 _internal/scripts/md2pdf.py <file.md>
```

---

## 🔗 참고

- [Exqutor 논문 (arXiv:2512.09695v2)](https://arxiv.org/abs/2512.09695v2)
- [Exqutor GitHub (BDAI-Research)](https://github.com/BDAI-Research/Exqutor)
- [캡스톤 사이트](https://capstone.cs.yonsei.ac.kr/capstone/)
- [팀 Notion HQ](https://www.notion.so/8110e4b8d680833a90bf01032872b1eb)
