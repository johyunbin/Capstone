# 회의 후 archive plan — 5/8 21:00+ KST

> 회의 종료 후 untracked 2건 + _drafts 정리. handoff §3-1 의 `archive/` 폴더에 통합.

---

## Untracked 2건 처리

### 대상
| 파일 | 사이즈 | mtime | 추정 정체 |
|---|---:|---|---|
| `__5_27__v3_Academic.zip` | 52 KB | 5/7 20:40 | 5/27 academic deck v3 source zip |
| `속도는벡터 — 5_27 최종발표 (v3 Academic).pdf` | 210 KB | 5/7 12:49 | 5/27 academic deck v3 export PDF |

### 처리 옵션

| 옵션 | 위치 | 사유 |
|---|---|---|
| **A** | `submission/_drafts/academic_deck_v3_source/` | deck source 와 함께 통합 (이미 같은 디렉토리에 source 존재) |
| **B** | `submission/_drafts/archive/` | archive 통합 (handoff §3-1 의 19 파일 archive 기준) |
| **C** | 그대로 유지 | 회의 후 v2 작성 시 reference 즉시 |

### **권장 = A** (academic_deck_v3_source/ 통합)
- 5/27 plan 자체가 회의 후 v2 로 작성될 예정
- v3 deck 은 v2 plan 의 source reference 로 academic_deck_v3_source/ 에 통합이 가장 정합

---

## 실행 명령 (사용자 결정 후, 옵션 A 기준)

```bash
cd /Users/hyunbin/Capstone

# 옵션 A: academic_deck_v3_source/ 로 이동
mv "__5_27__v3_Academic.zip" "submission/_drafts/academic_deck_v3_source/"
mv "속도는벡터 — 5_27 최종발표 (v3 Academic).pdf" "submission/_drafts/academic_deck_v3_source/"

# 또는 옵션 B: archive/ 통합
# mv "__5_27__v3_Academic.zip" "submission/_drafts/archive/"
# mv "속도는벡터 — 5_27 최종발표 (v3 Academic).pdf" "submission/_drafts/archive/"

# git add (회의 결과 commit 시 함께)
git add submission/_drafts/academic_deck_v3_source/ "__5_27__v3_Academic.zip" "속도는벡터 — 5_27 최종발표 (v3 Academic).pdf"
git status
```

---

## 추가 정리 후보 (회의 후)

### 1. _internal/ 임시 파일
- 회의 후 작업 종료 시:
  - `_internal/카톡_공유_초안_20260508_1830.md` → 회의 후 archive (메일 발송 완료 후)
  - `_internal/회의_진행가이드_20260508.md` → 회의 종료 후 _internal/archive/
  - `_internal/자문메일_발송체크리스트_20260508.md` → 자문 발송 후 _internal/archive/
  - `_internal/회의후_archive_plan_20260508.md` → 정리 완료 후 self-delete 또는 archive

### 2. handoff_v10 → archive
- 회의 후 handoff_v11 작성 시 v10 → `_internal/archive/`

### 3. _drafts/archive 통합 점검
- handoff §3-1 의 archive 19 파일 목록 + 본 회의 untracked 2건 = 21 파일
- 5/27 발표 후 추가 archive 예정 (회의 자료 v1 → archive)

---

## 회의 후 git commit 메시지 (옵션 A 기준)

```
W4 sprint 완료 인계 v10 + 회의 자료 정리

- 단일 10 cell × 31 method × RQ1/2/3 = 100% 측정 완료
- 4강 method ranking: HDBSCAN -8.04 / MB_partial -7.63 / Hilbert -7.54 / Hybrid -7.13
- 가지치기: Tier 1 17종 spread 1.21%p
- Sweet Spot 정량 boundary: cluster_ratio > 1.4 + intrinsic_dim < 0.85
- PDX (SIGMOD 2025) 학술 confirmation 추가
- multi 4강 일반화 측정 완료 (3 cell × 4 method × 5 sel)
- _drafts 정리: 5/27 academic deck v3 산출물 academic_deck_v3_source/ 통합
- PPT 양식 99% (Inter/JetBrains Mono/Pretendard 폰트 + 33 method funnel + spc XML)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

---

## 사용자 결정 항목 (회의 중 또는 후)

- [ ] 옵션 A / B / C 선택 (untracked 2건 처리)
- [ ] _internal 임시 파일 archive 시점 (회의 직후 / 회의 다음날)
- [ ] git commit message 수정 사항
