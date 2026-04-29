# _drafts — 팀과 공유할 작업본

이 폴더는 **현재 작업 중인 공유 문서** 를 둔다. 마감 후 정식 파일은 `submission/제출완료/` 로 이동하고, 작업 중간 버전은 `archive/` 로 보낸다.

> **마지막 갱신**: 2026-04-29 — 4/28 23:59 LearnUs 제출 완료 직후 (직속 파일 → `submission/제출완료/` 이동)

---

## 📌 현재 상태 (2026-04-29)

**작업 중인 활성 문서 없음.** 4/28 LearnUs 제출 완료, 4/30 발표 진행. 정식 제출본은 `submission/제출완료/` 참조:

- `속도는벡터_중간보고서.pdf` / `.docx` (18p)
- `속도는벡터_중간발표.pdf` / `.pptx` (17p)

다음 작업은 5/1~ RQ3 실험 결과 반영 → 최종발표(5/27~5/29) → 최종보고서(6/11) 순으로 이 폴더에서 진행.

---

## 📂 archive/ 구조

```
archive/
├── 자문이메일/         4/15 자문이메일 v1·v2 (md+pdf+docx)
├── 중간발표/           4/17~4/27 발표 자료 빌드 이력
│   └── templates/      디자인 변형 5종 백업 (academic·bold·editorial·gemini·glass)
├── 중간보고서/         v0~v3 반복 빌드 이력 (이동욱 v1, 조현빈 v2 등)
├── 팀원온보딩/         4/17·4/27·4/28 세 버전
└── 프로젝트설명서/     발표 스크립트, 예상질문, 사용설명서
```

---

## 🛠 빌드 명령 (RQ3 결과 반영 시 재사용)

```bash
# 마크다운 → PDF (Chrome CDP, 한글 OK)
python3 _internal/scripts/md2pdf.py "submission/_drafts/<파일>.md"

# 마크다운 → DOCX
python3 _internal/scripts/md2docx.py "submission/_drafts/<파일>.md"

# PPT 빌드 (디자인 변형 8종)
cd _internal/scripts/midterm_pptx && python3 build_academic.py <output.pptx>

# pptx → PDF (Keynote AppleScript)
./_internal/scripts/midterm_pptx/convert_pdf.sh <pptx 절대경로>
```

---

## 🔗 관련 문서

- 정식 제출본: `submission/제출완료/`
- 회의록: `_internal/records/kakaotalk/`
- RQ3 설계: `plans/RQ3설계안_20260416_213500.md`
- 실험 raw 데이터: `experiments/results/`
