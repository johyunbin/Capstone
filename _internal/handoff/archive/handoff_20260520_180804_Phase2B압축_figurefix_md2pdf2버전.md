# handoff 20260520 18:08 — Phase 2-B 보고서 압축 48→14p · figure 한글 폰트 fix · md2pdf 2 버전 분기 · 빈 여백 fix

> 이전 handoff(`_internal/handoff/archive/handoff_20260520_164600_캡스톤강의공지반영_세션종합.md`) → 본 문서. 이 문서 하나만 읽으면 0% loss 인계 — self-contained.
>
> **핵심 한 줄**: 본 세션(5/20 17:04~18:08)은 **Phase 2-B 보고서 본문 압축**(48p _162500 → **14p _171521** · 71% 축소) + **figure 5-1·5-2 한글 폰트 fix** (matplotlib Apple SD Gothic Neo 명시) + **md2pdf 2 버전 분기** (compact 제출용 + readable 내부 검토) + **빈 여백 fix** (subsection-keep 해제로 page 4·8 빈 여백 해결). 학교 양식 본문 14~22p 최저 충족 + 사용자 목표 18p 이하 도달. **정본 수치 17/17 모두 본문 보존** + **교수님 5/20 지적 12 항목 모두 충족**. **deferred**: 5/22 박광현 미팅 시각 확인·5/25 팀원 최종 검토·5/26 12:00 발표 자료 PPTX 마감·5/27+5/29 양일 발표·5/28 12:00 포스터·6/5 전시회·6/10 박광현 마지막 세미나·6/11 보고서 + 토요일 polish 4·발행 prompt 일괄·Phase 6 §6.4 통계 후속.

---

## 0. 가장 먼저 — 정본·진입점

- **★ 라우팅·구조 정본**: 루트 `CLAUDE.md`. anchor 본 handoff 로 갱신.
- **★ 보고서 신본 (정본 = compact 14p)**: `submission/_drafts/속도는벡터_6_11_최종보고서_20260520_171521.{md,pdf,docx}` — md 52KB · pdf 1.57MB 14p · docx 36KB. 학교 양식 14~22p 최저 충족. 정본 수치 17/17 모두 보존.
- **★ 보고서 readable 23p (carry, 내부 검토용)**: `submission/_drafts/속도는벡터_6_11_최종보고서_20260520_171521_readable.pdf` — margin 18mm·font 10.5pt·line-height 1.75·H2 마다 page break. 가시성 우선.
- **★ md2pdf 2 버전 (신규 분기)**:
  - `_internal/scripts/md2pdf.py` (compact 제출용 default) — margin 11/12mm · font 9.8pt · line-height 1.45 · H2 자연 흐름 · table padding 3-4px · subsection-keep auto
  - `_internal/scripts/md2pdf_readable.py` (readable 내부 검토) — margin 18mm · font 10.5pt · line-height 1.75 · H2 마다 break · subsection-keep avoid (git HEAD 원본)
- **★ analyze_latency.py figure 한글 폰트 fix**: matplotlib font.family = Apple SD Gothic Neo·NanumGothic·AppleGothic·DejaVu Sans 명시 + axes.unicode_minus=False. figure 5-1·5-2 재 생성 → `experiments/figures/보고서_6_11/fig5_2_speedup_heatmap.{png,pdf}` + `fig5_3_plan_recovery.{png,pdf}` 정상화.
- **★ 교수님 5/20 공지 정본 (carry)**: `_internal/state/캡스톤_교수님공지_20260520.md` — verbatim + 지적 12 항목
- **★ 일정 정본 (carry)**: `_internal/state/_schedule.md`
- **★ 직전 handoff (Phase 1·2·3·4·5 종합, carry)**: `_internal/handoff/archive/handoff_20260520_164600_캡스톤강의공지반영_세션종합.md`
- **★ 직전 보고서 _162500 (carry, 48p 원본)**: `submission/_drafts/속도는벡터_6_11_최종보고서_20260520_162500.{md,pdf,docx}`
- **★ v3 polish prompt (carry, 토요일 일괄 반영)**: `submission/_drafts/속도는벡터_발표deck_수정프롬프트_polish_20260520_144446.md` (polish 3 + 신규 polish 4 = B21 Acknowledgment 이름)
- **★ 토요일 발행 prompt 3종 (carry)**: `submission/_drafts/속도는벡터_{포스터,팜플렛,소개영상}_claudedesign_Phase2반영_20260520_100*.md`
- **★ v2 PPTX (carry, 5/22·5/26 자료 마감·5/27+5/29 발표 base)**: `submission/_drafts/속도는벡터_최종발표_슬라이드_phase2반영_v2.pptx` (1.20MB, 21장 raster image, ship-ready)
- **★ figure 5-5 (carry, 본문 통합 X)**: `experiments/figures/보고서_6_11/fig5_5_effect_size_distribution.{png,pdf}` — 효과크기 분포 4 panel
- **★ 서버 backup (carry, 직전 세션 산출, 5/21 권한 종료 후 보존 데이터)**: `_internal/server_backup_20260520/` (2.6G·22117 file)

## 1. 본 연구 framing (carry · 불변)

본 연구는 Exqutor 논문(arXiv:2512.09695v2) 재현이 아니라 **표본 선택(sample selection) 단계 하나**의 개입(무작위 Bernoulli → 분포 인지 stratification)이 추정 오차(Q-error)에 미치는 영향을 전 변인에 걸쳐 검증한 완전 실험 — 3-way matched B1(기존)·CaseA(완전 대체, 음성 대조군)·CaseB(결합, 산술평균). 발표물은 코드명(B1/CaseA/CaseB)·"영역" 필러·영어 메타 라벨·수식 노출 금지. 보고서는 코드명 사용 OK.

「엔진 적용 검증」 = 오프라인 검증된 카디널리티 추정치(13종 method 결합 = CaseB ×13)를 패치된 PostgreSQL(서버 55435)에 주입해 "추정치 → 실행 계획 → end-to-end latency" 고리를 닫는 실험. 4조건: 기본엔진(baseline) / 베이스라인(B1) / 결합(CaseB ×13) / 오라클(true_card).

## 2. 본 세션(5/20 17:04~18:08)이 한 일

| 항목 | 상태 | 내용 |
|---|---|---|
| 직전 handoff 정독 + 사용자 결정 (~18p 압축) | ✅ | handoff_164600 흡수 + 새 세션 진입 + AskUserQuestion 으로 ~18p 목표 확정 (다른 옵션: ~14p·~10p·~20p) |
| Phase 2-B 보고서 압축 plan + ExitPlanMode 승인 | ✅ | `/Users/hyunbin/.claude/plans/jiggly-sniffing-waterfall.md` 작성 — 본문 압축 strategy·정본 17건·figure 처리·section 별 line target. 사용자 승인. |
| 1차 압축 _171521.md 작성 + pdf/docx 빌드 | ✅ | 48p → 29p (40% 축소) · md 110KB → 57KB. 정본 수치 17/17 보존. 페이지 수 18p 목표 +11p 초과 — H2 강제 page break (11 H2 = 최소 11p) 원인. |
| CSS 수정 + 추가 narrative 압축 → 21p | ✅ | md2pdf.py CSS 수정 (margin 18→15mm·font 10.5→10pt·line-height 1.75→1.5·H2 page-break 제거·table padding 6→3px·font 9→8.5pt). 추가 압축 (목차 제거·§3.6·§4.5·§5.4·§7.1 narrative 트림). → 21p (학교 양식 22p 상한 충족) |
| 추가 narrative 트림 + figure 제거 → 20p → 17p | ✅ | figure 1-1·4-2·7-1 reference 제거 (3 figure 파일은 carry). §4.7·§5.5 honest limitation bullet 화. CSS margin 13→11/12mm·font 9.8pt 으로 추가 컴팩트. → 17p (사용자 18p 이하 도달) |
| ★ 사용자 PDF 시각 점검 결과 흡수 | ✅ | "빈 여백 너무 많은 페이지 + figure 폰트 깨지거나 텍스트 겹치거나" 지적 → PDF 17p 전수 점검 (Read pdf pages 1-10, 11-17). 발견: page 4·8 빈 여백 + figure 5-1·5-2 한글 깨짐 (□ 사각형). |
| Phase F1 — figure 5-1·5-2 한글 폰트 fix | ✅ | `_internal/scripts/analyze_latency.py` 에 matplotlib.rcParams font.family = Apple SD Gothic Neo·NanumGothic·AppleGothic·DejaVu Sans 명시 + axes.unicode_minus=False. phase2 데이터로 재 생성 → `experiments/figures/보고서_6_11/fig5_2_speedup_heatmap.{png,pdf}` + `fig5_3_plan_recovery.{png,pdf}` 갱신. 한글 "baseline 대비 speedup — cell × variant" + "실행 계획 회복 — oracle 과 동일 plan 여부" + 범례 "=oracle ●·≠oracle·미캡처/MISS" 정상 표시 확인. |
| Phase F2 — md2pdf 2 버전 분기 | ✅ | `_internal/scripts/md2pdf.py` (compact 제출용 default) + `_internal/scripts/md2pdf_readable.py` (readable 내부 검토 = git HEAD 원본 복사) 분기. 두 버전 동시 빌드 + 비교 — compact 17p / readable 23p. docstring 명시. |
| Phase F3 — compact 빈 여백 fix (subsection-keep 해제) | ✅ | `div.subsection-keep { page-break-inside: avoid }` 가 §3.2(figure 3-1)·§4.3(16-method 표) 같은 큰 block 을 통째 다음 페이지로 push 하여 page 4·8 큰 빈 여백 발생. compact CSS 만 `auto` 로 변경 (readable 은 carry). **17p → 14p 추가 압축 + 모든 페이지 빽빽 채워짐**. |
| 최종 PDF 14p 시각 점검 | ✅ | Page 1-14 전수 점검: 모든 페이지 빈 여백 없음 + figure 5-1·5-2 한글 정상 + 정본 수치 본문 노출 (89.1%·−4.38%·5.67×·94.9%·148/156·180/180·86.9% 등). |
| docx 재 빌드 + draft 정리 | ✅ | pandoc 으로 docx 갱신 (36KB) + draft 정리 (_171521_compact.pdf 17p 중간 백업 제거) |
| ★ 사용자 지적 양식 점검 (보고서 12 항목) | ✅ | 교수님 5/20 마지막 강의 transcript verbatim 흡수 + 12 항목 점검표 작성: §1=Introduction·Abstract 1p·Background/Related Work 분리·Acronym 풀이·TOC carry·Future Work·"진행=결과"·계획≠EC·헤드라인↔본문·페이지 14~22p·역할 분담·지도교수/석사/멘토 이름. **12/12 모두 충족** 확인. |
| 종료 — handoff·archive·CLAUDE.md anchor·commit·push | (진행 중) | 본 file + 새세션 복붙 프롬프트 + 직전 _164600 archive + CLAUDE.md anchor 갱신 + commit + push + gh run watch. 메모리 갱신 별도. |

## 3. ★★★ 본 세션 결과 — 다음 세션이 반드시 흡수할 정본

### 3.1 보고서 최종 신본 _171521

| 항목 | 값 |
|---|---|
| compact pdf 페이지 | **14p** (학교 양식 14~22p 최저 충족) |
| readable pdf 페이지 | 23p (내부 검토용, 학교 양식 상한 약간 초과) |
| 원본 _162500 대비 압축 | 48p → 14p (71% 축소) |
| md size | 110KB → 52KB (53% 축소) |
| 정본 수치 보존 | **17/17** (89.1%·1,344·−4.38%·−3.06%·−4.09%·65.3%·72.1%·35.2%·+12.90%·5.67×·2,880·7/12·148/156·94.9%·180/180·13/168·7.7%·146/168·86.9%·plan_signature·Node Type·0.93×·honest exception·N=385·m=0.9·chao_weighted·−6.22%·11.03·sparse_rp·2.91·16 method·7 paradigm·1,508) |
| figure 보존 | 5 (2-1·3-1·4-1·5-1·5-2) ← 14 figure 중 9 reference 제거, 파일은 carry |
| 교수님 5/20 지적 12 항목 충족 | **12/12** |

### 3.2 교수님 5/20 지적 vs 신본 _171521 매핑

| 지적 | 신본 반영 | 위치 |
|---|---|---|
| §1 = Introduction (Background X) | ✅ §1.1 "연구 주제 및 목표" | §1.1 |
| Abstract 1 paragraph (high-level) | ✅ 5문장 1 paragraph | line 24 |
| Background ≠ Related Work | ✅ §2.1 "기존 시스템 (Background)" / §2.2 "관련 연구 (Related Work) — Exqutor §V-B Adaptive Sampling" | §2.1·§2.2 |
| Acronym 풀어쓰기 | ✅ VAQ·VBASE·TPC-H·SeqScan·ECQO·HNSW·SSN·IVF 처음 등장 시 풀이 | 곳곳 |
| TOC 짧은 보고서 불필요 | ✅ 제거 (compact 14p 에서 TOC 없음) | — |
| Future Work (다른 사람 이어갈) | ✅ §6.4 4 갈래 | §6.4 |
| "진행 = 결과" 수치 위주 | ✅ §4 1,508건·§5 2,880회 latency | §4·§5 |
| 계획 ≠ Expected Contribution | ✅ §7.1·§7.2 | §7 |
| 헤드라인 ↔ 본문 매칭 | ✅ section 헤드라인 ↔ 내용 일치 | 곳곳 |
| 페이지 길이 학교 양식 14~22p | ✅ 14p (최저 충족) | — |
| 역할 분담 명시 ("다같이" X) | ✅ §7.2 4인 분담 표 7-1 | §7.2 |
| 지도교수·석사·멘토 이름 | ✅ §8 박광현·임채림·박성원 | §8 |

### 3.3 md2pdf 2 버전 차이

| 항목 | compact (제출용) | readable (내부 검토) |
|---|---|---|
| 파일 | `_internal/scripts/md2pdf.py` | `_internal/scripts/md2pdf_readable.py` |
| margin | 11/12mm | 18mm |
| font-size | 9.8pt | 10.5pt |
| line-height | 1.45 | 1.75 |
| H2 page-break-before | 자연 흐름 | 항상 (새 페이지) |
| table padding/font | 3-4px / 8.5pt | 6-7px / 9pt |
| table page-break-inside | auto (분리 허용) | avoid |
| subsection-keep | auto | avoid (짤림 방지) |
| 동일 md 페이지 수 | **14p** | 23p |
| 용도 | 학교 제출 (14~22p 충족) | 내부 검토·단행본·풀 학술 톤 |

### 3.4 figure 5-1·5-2 한글 폰트 fix

`_internal/scripts/analyze_latency.py` 추가 코드 (line 27-31):
```python
plt.rcParams["font.family"] = ["Apple SD Gothic Neo", "NanumGothic", "AppleGothic", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
```

재 생성된 figure (전 한글 정상 표시):
- `experiments/figures/보고서_6_11/fig5_2_speedup_heatmap.{png,pdf}` — 제목 "baseline 대비 speedup — cell × variant"
- `experiments/figures/보고서_6_11/fig5_3_plan_recovery.{png,pdf}` — 제목 "실행 계획 회복 — oracle 과 동일 plan 여부" + 범례 "=oracle ●·≠oracle·미캡처/MISS"

### 3.5 5/20 16:15 + 17:04~18:08 추가 강의 transcript 흡수 — 일정·발표·전시 verbatim

- **5/26 (화) 11:59 PM Learnus** — **발표 자료 (PPTX)** 마감. 늦지 않게 미리미리 제출.
- **5/27 (수) + 5/29 (금)** — 양일 분산 최종 발표 · 5/27 수업 때 발표 순서 공지 · 최대 10분 · Q&A · **무단 결석 = 발표 점수 0점** · 가산점 = 질문
- **5/28 (목) 12:00 정오** — 전시 포스터 PDF 제출 (900×1200mm, 세로) · 영상 3~5분 자막 + YouTube + QR 코드 포스터 박기 (없을 시 감점)
- **6/5 (금) 9~18시** — 졸업 전시회 제5공학관 1층 로비 · 504호 15:00 집결 · 인기상 투표 · 자기팀 X
- **6/10 (수)** — 박광현 마지막 세미나
- **6/11 (목)** — 최종 보고서 + 상호평가 결과 (Learnus 마감)
- 상호평가 3차 5/26 · 4차 6/9
- 보고서 길이: 너무 짧지도 너무 길지도. 학교 양식 14~22p. AI 길이 부풀리기 금지.

## 4. ★ 다음 세션 task

1. **[★시급·5/22 미팅 base] 보고서 _171521 + v2 deck 사용자 시각 확인**:
   - compact pdf 14p PowerPoint·Adobe Reader 렌더 정상 확인
   - readable pdf 23p 도 확인 (내부 검토 base)
   - v2 PPTX 21장 ship-ready (carry)
2. **[★ 5/25 까지] 보고서 _171521 신본 팀원 최종 검토**:
   - Abstract 1 paragraph 확인
   - §2.1 "기존 시스템 (Background)" + §2.2 "관련 연구 (Related Work)" 표제 확인
   - §8 감사의 글 (박광현·임채림·박성원) 확인
   - VBASE/TPC-H/SeqScan acronym 풀이 확인
   - 14p 가 학교 양식 충족 확인
3. **[★ 5/26 (화) 11:59 PM] 발표 자료 PPTX Learnus 제출**:
   - v2 PPTX (carry · ship-ready · 1.20MB · 21장) Learnus 업로드
   - 정시 마감 — 늦지 않게
4. **[★ 5/27·5/29 발표 양일] 무단 결석 = 발표 점수 0점**:
   - 5/27 수업 때 발표 순서 공지
   - 가산점 = 다른 팀 발표 시 질문하기
5. **[★ 토요일·사용자 직접·claude.ai/design 한도 복구 후] 발행 자료 4종 일괄 export**:
   - polish 3건 (B13·B19·B2, carry prompt) + **polish 4 신규** (B21 Acknowledgment 이름) → v3 deck
   - 포스터·팜플렛·영상 3 prompt (carry)
   - 영상 녹화 → 자막 burn-in → YouTube 업로드 → QR 코드 → 포스터·팜플렛에 박기
   - **포스터·팜플렛 PDF 900×1200mm 세로 제출 (5/28 12:00 정오 마감)**
   - export 후 본 세션 5축 vision 재검증 (sub-agent 5 launch pattern carry)
6. **[★ 6/5 금 전시회] 504호 15:00 집결**:
   - 함께 내려가서 관람·투표 (자기팀 X)
   - 인기상 상품
7. **[6/10 박광현 마지막 세미나 + 6/11 최종 보고서·상호평가 결과 (Learnus 마감)]**
8. **[후속·6/11 까지] Phase 6 §6.4 통계 후속 PoC** — plan-level effect size / cluster bootstrap / variance decomposition

## 5. 서버 접속·실행 (★ 5/21 권한 종료)

- 접속: `ssh capstone` (165.132.140.240). PG: `PGPASSWORD=wns41559 psql -h localhost -p 55435 -U wns41559 -d wns41559`.
- ⚠️ **`build_custom.sh`/`apply_patch.sh` 절대 금지** — 재빌드 필요 시 직접 빌드.
- ★ **서버 권한 5/21 (수) 까지** — 직전 세션이 backup 으로 핵심 데이터 (2.6G/22117 file) 로컬 보존. 권한 종료 후에도 backup 으로 4 엔진 통합 PoC·재현 검증 가능.

## 6. 산출물 경로 (본 세션 신규 + carry)

| 산출물 | 경로 | 상태 |
|---|---|---|
| **★ 보고서 신본 _171521 (compact 14p, 정본)** | `submission/_drafts/속도는벡터_6_11_최종보고서_20260520_171521.{md,pdf,docx}` | 정본 (52KB md / 1.57MB pdf / 36KB docx) |
| ★ 보고서 readable 23p (carry, 내부 검토) | `submission/_drafts/속도는벡터_6_11_최종보고서_20260520_171521_readable.pdf` | carry (1.59MB) |
| 직전 보고서 _162500 (carry, 원본 48p) | `submission/_drafts/속도는벡터_6_11_최종보고서_20260520_162500.{md,pdf,docx}` | carry |
| 이전 _144446·_124200 (carry) | `submission/_drafts/속도는벡터_6_11_최종보고서_20260520_{144446,124200}.{md,pdf,docx}` | carry |
| **★ md2pdf 2 버전 분기 (신규)** | `_internal/scripts/{md2pdf.py,md2pdf_readable.py}` | 신규 (compact default + readable carry) |
| **★ analyze_latency.py figure 한글 폰트 fix** | `_internal/scripts/analyze_latency.py` | 갱신 (rcParams font.family 명시) |
| **★ figure 5-1·5-2 재 생성** | `experiments/figures/보고서_6_11/fig5_2_speedup_heatmap.{png,pdf}` + `fig5_3_plan_recovery.{png,pdf}` | 갱신 (한글 정상) |
| 일정 정본 (carry) | `_internal/state/_schedule.md` | carry |
| 교수님 공지 정본 (carry) | `_internal/state/캡스톤_교수님공지_20260520.md` | carry |
| figure 5-5 효과크기 (carry, 본문 통합 X) | `experiments/figures/보고서_6_11/fig5_5_effect_size_distribution.{png,pdf}` | carry |
| v3 polish prompt (carry) | `submission/_drafts/속도는벡터_발표deck_수정프롬프트_polish_20260520_144446.md` | carry |
| 토요일 발행 prompt 3종 (carry) | `submission/_drafts/속도는벡터_{포스터,팜플렛,소개영상}_claudedesign_Phase2반영_20260520_100*.md` | carry |
| v2 PPTX (carry · ship-ready) | `submission/_drafts/속도는벡터_최종발표_슬라이드_phase2반영_v2.pptx` | carry |
| 서버 backup (carry) | `_internal/server_backup_20260520/` (2.6G·22117 file) | carry |
| archive 이동 (본 세션) | `_internal/handoff/archive/handoff_20260520_164600_*` + `새세션_복붙_프롬프트_20260520_*` | 완료 |

CLAUDE.md anchor 갱신: **본 handoff (`handoff_20260520_180804_Phase2B압축_figurefix_md2pdf2버전.md`)** + 보고서 신본 _171521 anchor.

## 7. carry-forward / 보류 / 미커밋 (본 세션 직후)

- **★ 본 세션 commit 대상**:
  - `submission/_drafts/속도는벡터_6_11_최종보고서_20260520_171521.{md,pdf,docx}` (신규 — compact 14p 정본)
  - `submission/_drafts/속도는벡터_6_11_최종보고서_20260520_171521_readable.pdf` (신규 — readable 23p)
  - `_internal/scripts/md2pdf.py` (수정 — compact CSS)
  - `_internal/scripts/md2pdf_readable.py` (신규 — readable git HEAD 복사)
  - `_internal/scripts/analyze_latency.py` (수정 — matplotlib 한글 폰트)
  - `experiments/figures/보고서_6_11/fig5_2_speedup_heatmap.{png,pdf}` + `fig5_3_plan_recovery.{png,pdf}` (갱신)
  - `_internal/handoff/active/handoff_20260520_180804_*.md` (신규)
  - 새세션 복붙 프롬프트 `_internal/handoff/active/새세션_복붙_프롬프트_20260520_180804.md` (신규)
  - `_internal/handoff/archive/handoff_20260520_164600_*` (이동)
  - `CLAUDE.md` (anchor 갱신)
- **이번 세션 commit + push + gh run watch** (사용자 명시 동의)
- **메모리 갱신** (사용자 별도 sync 필요)
- **deferred tool 로드 패턴**: 새 세션은 `ToolSearch select:TaskCreate,EnterPlanMode,ExitPlanMode,Monitor,TaskUpdate,TaskList` 선제 로드

## 8. ★ 환각 회피 룰 (carry, 본 세션 신규 추가)

- 정본 수치 정합 = `_internal/cache/rq3/latency/{phase2,phase3}/figures/paired_stats.csv` (15 컬럼) + 보고서 §5.5 표 5-3 + figure 5-5 (carry).
- **B1 plan 회복은 qid 의존 fragile (7/12)** — qid=0 만으로 generalize 금지.
- **CaseB > B1 latency 측면 우열은 없음** (paired Wilcoxon 7.7% 유의, 효과크기 86.9% small g). plan 회복 robustness 측면 우위만 강조.
- **Q12 qid 0 large effect (g ≈ −1.5)** — 같은 4 method 의 qid 1·qid 2 는 small (g < 0.4), p_holm = 1.0.
- **core 4 cell sel=0.001 한정 → phase3 carry-over sel=0.01·0.1**: baseline sel=0.01 모두 large (60/60), sel=0.1 모두 small. B1 sel=0.01·0.1 모두 small (≈ 90%). 선택도 임계점 명시.
- **plan_signature 정의 = Node Type pre-order 튜플 (1-tuple)** — 보고서 정정 완료 (carry).
- **q9 sel=0.1 honest exception** — plan ≠ baseline 인데 speedup < 1.0 (0.93×). 보고서 §6.4 (1) 갈래 carry.
- **★ 교수님 공지 (carry)**: 전시회 6/5 금 / 발표 5/27+5/29 양일 / 자료 PPTX 5/26 11:59 PM Learnus / 포스터 5/28 12:00 정오 / 무단결석 0점 / 가산점=질문.
- **★ 본 세션 신규 carry — 보고서 정본 = _171521 compact 14p**: 정본 17/17 + 교수님 12/12 모두 충족. _162500 (48p) 는 carry. ECQO 풀명 = "Exact Cardinality Query Optimization" (원논문 verbatim) 유지.
- **★ 본 세션 신규 carry — md2pdf 2 버전 분기**: compact (default) vs readable (md2pdf_readable.py). 학교 제출은 compact, 내부 검토는 readable.
- **★ 본 세션 신규 carry — figure 5-1·5-2 한글 폰트 fix**: analyze_latency.py 의 matplotlib rcParams 명시. 향후 figure 재 생성 시 한글 깨짐 X.
- **★ 본 세션 신규 carry — Phase 2-B 완료**: 사용자 목표 18p 이하 달성 (14p). 다음은 5/22·5/25·5/26·5/27·5/28·6/5·6/10·6/11 일정 라인.
- **★ polish 4 후보 (carry)**: B21 종결 슬라이드 Acknowledgment 이름 (박광현·임채림·박성원). 토요일 v3 deck rebuild 시 일괄 반영.
- 보고서 코드명(B1/CaseA/CaseB) 사용 OK / 발표물 코드명 노출 금지 — v2 검증 결과 0건 carry.
- v2 = raster image PPTX (vision 검증만) carry — v3 polish 도 raster image PPTX 형식 예상.

---

작성: 2026-05-20 18:08 KST — 본 세션 (Phase 2-B 압축 48→14p + figure 한글 폰트 fix + md2pdf 2 버전 분기 + 빈 여백 fix) 완료. 보고서 신본 _171521 (compact 14p · readable 23p) · figure 5-1·5-2 한글 정상. → 다음 = 5/22 미팅·5/25 팀원 검토·5/26 PPTX Learnus 마감·5/27+5/29 발표·5/28 12:00 포스터·6/5 금 전시회·6/10 박광현 세미나·6/11 보고서. Phase 6 (§6.4 통계 후속) deferred.
