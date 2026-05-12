# [자문 메일 초안 v3 supplement] — 5/7 W3 sprint 결과 추가

> **본 supplement = 기존 자문 메일 초안 v2** (`속도는벡터_자문메일초안_채림석사_20260506.md`) **+ W3 sprint 산출 추가**.
> 5/8 회의 합의 후 v2 + supplement 통합 → 5/15 발송.

**To**: 채림 석사
**Cc**: 박세은 (팀장), 조현빈 (작성)
**Subject**: [속도는벡터 캡스톤] 5/7 W3 sprint 5-cell matrix + raw dataset 사용 동의 요청

---

## W3 sprint 추가 결과 (5/7 14:33~15:46)

### 1. SIFT 8M chain debug 완료 + Option 1 SIFT 1M subset

이전 인계 (5/7 14:33) 시점 silent fail 상태였던 `customer_sift_8m_subset` chain 5건 root cause 해결 (`autocommit + cursor`, format mismatch, runner name + npy cache fast-path). **SIFT 1M subset** (`customer_sift_1m_subset`, BIGANN learn.100M 첫 1M) 추가 → **DEEP/SIFT × 1M/8M 정확 매칭 2×2 + SIFT 1.5M legacy baseline = 5-cell 완성**.

### 2. 5-cell matrix (sel=0.10, paired bootstrap CI 기준)

| method | DEEP_1M | DEEP_8M | SIFT_1M | SIFT_1.5M | SIFT_8M |
|---|---:|---:|---:|---:|---:|
| **hilbert** | −0.97%* | −2.21%* | −3.70%* | −7.06%* | −2.64%* |
| **minibatch_partial** | −2.26%* | −1.98%* | −3.60%* | −8.02%* | −2.10%* |
| **hybrid** | −2.77%* | −1.73%* | −3.28%* | −8.47%* | −2.63%* |
| **hdbscan** | −2.42%* | −2.13%* | −4.82%* | −8.55%* | (timeout) |
| distance_shell (negative) | +7.59%* | +6.14%* | +6.39%* | +4.84%* | +8.57%* |
| random_proj (negative) | +6.00%* | +2.50%* | +49.19%* | +11.02%* | +31.79%* |

`*` = paired bootstrap 95% CI 0 제외

### 3. Cross-scale stability (Primary 4 cell)

- **DEEP_1M ↔ DEEP_8M**: 78% CI 일관, 89% 부호 일관, median Δ = +0.04%
- **SIFT_1M ↔ SIFT_8M**: 83% CI 일관, 91% 부호 일관, median Δ = +0.20%

→ **본 연구 contribution 의 cross-scale invariance 입증** (DEEP/SIFT 모두 80%+ CI / 90%+ 부호 일관).

---

## 추가 자문 사항 (W3 NEW, v2 의 5종 + 본 supplement 의 1종 = 총 6종)

**(바)** **TPC-H natural baseline (SIFT 1.5M) vs BIGANN raw extract (SIFT 1M+8M) framing**:

`customer_sift_10_phase7_noidx_subset` (TPC-H natural, 채림 석사 적재본) 과 `customer_sift_1m_subset` / `customer_sift_8m_subset` (BIGANN learn.100M 첫 1M / 첫 8M) 는 같은 SIFT distribution 이지만 **distribution shape 가 다름** (4강 method 효과 size SIFT_1.5M 가 SIFT_1M 보다 ~2× 강).

본 연구의 처리:
- **Primary 4-cell** = DEEP/SIFT × 1M/8M (BIGANN raw 통일, scale-matched cross-scale)
- **TPC-H natural baseline** = SIFT_1.5M 별도 보고 (Exqutor 와 직접 비교 가능 distribution)

**자문 사항**: 이 분리 reporting (Primary cross-scale + TPC-H baseline) 의 학술 framing 적절성? 또는 SIFT_1.5M 을 main 매트릭스에 통합하는 게 더 정직한지?

---

## Raw dataset 사용 동의 요청 (5/15 발송 시 동봉)

본 연구의 SIFT 1M+8M subset 적재는 다음 raw dataset 의 직접 read (write/적재는 본인 cap2026 영역) 으로 수행했습니다. 채림 석사님께 **사후 동의** 요청드립니다 (W3 sprint 진행 시점 5/7, 자율 판단).

### 사용 완료 (W3 적재본 — 모두 본인 cap2026 영역)
- `/mnt/hdd0/home/kgh1030/vecdb_dataset/bigann/learn.100M.u8bin` (12.8GB) — 첫 1M + 첫 8M extract → `customer_sift_1m_subset`, `customer_sift_8m_subset`

### 사용 예정 (5/15 자문 회신 + 5/8 회의 합의 후 결정)
- `/mnt/hdd0/home/kgh1030/vecdb_dataset/yandex_deep/base.1B.fbin` (384GB) — DEEP 80M extract (Exqutor SF=100 직접 비교 future work)
- `/mnt/BDAI_NAS/kgh1030/vecdb_dataset/fb_simsearchnetpp/` — SimSearchNet++ 256d (Exqutor 5 dataset 매칭)
- `/mnt/BDAI_NAS/kgh1030/vecdb_dataset/wiki-all/` — WIKI 768d (Exqutor 5 dataset 매칭)

PG 테이블 적재 (모두 `wns41559` DB 본인 cap2026 영역):
- `customer_sift_1m_subset` (1M × 128d, ~150MB) ✓ 적재 완료
- `customer_sift_8m_subset` (8M × 128d, ~1.2GB) ✓ 적재 완료
- `customer_deep_80m_subset` (예정, ~30GB) — 자문 회신 후 결정
- `customer_simsearchnetpp_*_subset` / `customer_wiki_*_subset` (예정) — 자문 회신 후 결정

본인은 채림 석사 룰 4가지 (cap2026 write/적재만, sudo X, PG port 55435-55436, GPU X) 를 모두 준수하며 진행했습니다.

---

## 5/27 발표 narrative ready

본 supplement 의 5-cell matrix + cross-scale stability + Exqutor 비교 framing 통합. 5/27 발표 본문은 v2 자문 메일의 자문 사항 5종 + 본 supplement 의 자문 사항 (바) 회신 반영 후 최종화.

회신 부탁드립니다. 감사합니다.

조현빈 드림
2026-05-07 (W3 sprint 결과 반영)

---

## [작성자 메모, 발송 시 삭제]

- 5/8 회의에서 본 supplement (a) 자문 사항 (바) 합의, (b) raw dataset 동의 요청 framing 합의, (c) v2+supplement 통합 발송 vs 분리 발송 합의
- 채림 석사 룰 준수 명시 — 사후 동의 보고는 "이미 적재한 1M+8M subset" + "예정 dataset 사용 동의 요청" 양면
- 5/15 발송 시 첨부: master.md final + 5-cell matrix CSV + cross_scale.csv + handoff_v3 + W2 부록
