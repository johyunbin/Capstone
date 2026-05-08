# Worker D — RQ1 Phase 6/7 5-cell 비교 figure 생성 (Slide 4/6 footnote 보강)

> **임무**: `rq1_phase6_vs_phase7_comparison.json` 의 5-cell raw 결과 → matplotlib figure (5/27 발표 Slide 4 또는 Slide 6 footnote 보강용 + 자문 메일 첨부 보강).
> **세션 진입**: 본 핸드오프 첫 read → JSON read → figure 작성.
> **manager 세션**: 2026-05-07 11:20 KST, Opus 4.7 1M.

---

## 1. 입력 자료

| 파일 | 위치 | 핵심 |
|------|------|------|
| Phase 6/7 비교 raw | [experiments/results/rq1_motivation/rq1_phase6_vs_phase7_comparison.json](../experiments/results/rq1_motivation/rq1_phase6_vs_phase7_comparison.json) | 5 cell × 2 mode (Phase 6 SQL / Phase 7 numpy) |
| Master 표 | [experiments/results/RQ1_RQ2_RQ3_종합_master.md](../experiments/results/RQ1_RQ2_RQ3_종합_master.md) (line 81-99) | 5-cell 표 + per-seed ρ |
| Korean matplotlib helper | `experiments/code/local_analysis/_matplotlib_korean.py` | 한글 폰트 적용 |

## 2. 작업 단계

### Step 1 (10분) — JSON 구조 확인

```python
import json
with open('experiments/results/rq1_motivation/rq1_phase6_vs_phase7_comparison.json') as f:
    data = json.load(f)
print(list(data.keys()))
# 5 cell: s=0.01 / 0.05 / 0.10 / 0.30 / 0.50
# 각 cell: phase6 / phase7 의 (KM20, BERN, RANDOM20) mean + se
```

JSON 구조 확인 후 figure plan 결정.

### Step 2 (45분) — Figure 작성

**Figure 1**: Phase 6 vs Phase 7 5-cell bar chart
- x축: 5 sel (0.01 / 0.05 / 0.10 / 0.30 / 0.50)
- y축: KM20-BERN diff (%)
- 2 group: Phase 6 (SQL D, dark navy) / Phase 7 (numpy D, light gray)
- annotation: 각 bar 위 수치, 5-cell 격차 (Δ) 별도 표기

**Figure 2** (선택): Per-seed Spearman ρ scatter
- Phase 6: ρ=−0.680 [−0.800, −0.440] (errorbar, dark navy)
- Phase 7: ρ=+0.240 [−0.061, +0.480] (errorbar, light gray)
- horizontal line at 0 (no monotonic)
- annotation: "CI 0 제외 (Phase 6) vs CI 0 포함 (Phase 7)"

**Figure 3** (선택): 단조성 trend line plot
- x축: log(sel)
- y축: KM20-BERN diff (%)
- 2 line: Phase 6 (solid) / Phase 7 (dashed)
- shaded region: bootstrap CI

```python
import matplotlib.pyplot as plt
import numpy as np
from experiments.code.local_analysis._matplotlib_korean import set_korean

set_korean()

# 데이터 (master.md 표 line 86-91 기준)
sels = [0.01, 0.05, 0.10, 0.30, 0.50]
phase6 = [+8.93, +1.85, -2.06, -3.11, -10.67]
phase7 = [+3.33, -2.60, -1.31, -0.99, -1.23]

fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
x = np.arange(len(sels))
width = 0.35

bars1 = ax.bar(x - width/2, phase6, width,
               label='Phase 6 (SQL D, vector.c hook, production-near)',
               color='#1B365D', edgecolor='white')
bars2 = ax.bar(x + width/2, phase7, width,
               label='Phase 7 (numpy D, simulation)',
               color='#A0A0A0', edgecolor='white')

# Annotations
for bar in bars1 + bars2:
    h = bar.get_height()
    ax.annotate(f'{h:+.2f}%',
                xy=(bar.get_x() + bar.get_width()/2, h),
                xytext=(0, 3 if h > 0 else -12),
                textcoords='offset points',
                ha='center', va='bottom' if h > 0 else 'top',
                fontsize=9)

ax.axhline(0, color='black', linewidth=0.5)
ax.set_xticks(x)
ax.set_xticklabels([f's={s:g}' for s in sels])
ax.set_xlabel('Selectivity')
ax.set_ylabel('KM20 − BERN diff (%)')
ax.set_title('RQ1 Phase 6 vs Phase 7 — DEEP 1M KM20-BERN Selectivity Gradient (5/7 W2)')
ax.legend(loc='lower left', framealpha=0.9)
ax.grid(axis='y', alpha=0.3)

# 5-cell 격차 annotation
for i, (p6, p7) in enumerate(zip(phase6, phase7)):
    delta = p6 - p7
    ax.annotate(f'Δ={delta:+.2f}%p',
                xy=(i, max(p6, p7) + 1.5),
                ha='center', fontsize=8, color='red',
                fontweight='bold')

# per-seed ρ footnote
fig.text(0.5, 0.02,
         'per-seed Spearman ρ — Phase 6: −0.680 [−0.800, −0.440] CI 0 제외 (단조 감소 확정) · '
         'Phase 7: +0.240 [−0.061, +0.480] CI 0 포함 (검정력 약화)',
         ha='center', fontsize=9, style='italic')

plt.tight_layout(rect=[0, 0.03, 1, 1])
plt.savefig('experiments/figures/rq1_motivation/phase6_vs_phase7_5sel.png',
            dpi=300, bbox_inches='tight')
plt.close()
```

### Step 3 (15분) — Figure 검증 + commit

```bash
# 한글 폰트 깨짐 X 확인
open experiments/figures/rq1_motivation/phase6_vs_phase7_5sel.png

# commit
git add experiments/figures/rq1_motivation/phase6_vs_phase7_5sel.png
git commit -m "RQ1 Phase 6 vs Phase 7 5-cell 비교 figure (Slide 4/6 footnote 보강)"
git push
```

### Step 4 (선택, 30분) — md narrative 첨부 작성

자문 메일 첨부용 PDF (Worker B/C 가 사용):
- `experiments/results/rq1_motivation/phase6_vs_phase7_5sel.md`
  - figure 삽입 + 5-cell 표 + per-seed ρ + origin 두 가지 + 본 연구 처리 (옵션 2)
- `python3 _internal/scripts/md2pdf.py phase6_vs_phase7_5sel.md` → PDF

## 3. 산출 spec

| 산출 | 위치 | 형식 |
|------|------|------|
| Figure 1 (필수) | `experiments/figures/rq1_motivation/phase6_vs_phase7_5sel.png` | PNG 300dpi, A4 landscape 적합 |
| Figure 2/3 (선택) | `experiments/figures/rq1_motivation/phase6_vs_phase7_rho.png` 등 | PNG |
| md 첨부 (선택) | `experiments/results/rq1_motivation/phase6_vs_phase7_5sel.md` | PDF 변환 후 자문 첨부 |

## 4. 검증 기준

- [ ] 한글 폰트 적용 (Apple SD Gothic Neo)
- [ ] 5 cell 수치 정확 (master.md 표 line 86-91 일치)
- [ ] per-seed ρ footnote (Phase 6 −0.680 / Phase 7 +0.240)
- [ ] Δ annotation (5 cell 의 격차 표기)
- [ ] 색 대비 (Phase 6 dark navy, Phase 7 light gray) — Academic deck 톤 일관

## 5. 의존성

- **Worker A (PPT)**: figure 완료 후 Slide 4/6 footnote 에 삽입 (sync)
- **Worker B/C (자문 메일)**: figure md 첨부 활용 (선택)

## 6. 예상 시간

총 1h (필수 figure 1) ~ 1.5h (보조 figure + md 첨부 포함).

## 7. 본 worker 가 만들지 말 것

- 새 측정 진행 (rq1_phase6_vs_phase7_comparison.json 의 raw 만 활용)
- Phase 7 수치 임의 변경 (옵션 2 narrative 정직 reporting 보존)
- 색 / layout 의 큰 변경 (Academic deck 일관성 유지)

---

**작성**: Claude (manager session, Opus 4.7 1M) · 2026-05-07 11:20 KST
**기반**: rq1_phase6_vs_phase7_comparison.json (5/7 W2 발견) + master commit 74d6aea
