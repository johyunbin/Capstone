#!/bin/bash
# 통합 측정 캠페인 마스터 v2 — 5/17 세션 (전권 위임, 정확성 우선).
# task A verdict 후속: measure_case_b 의 est_b1 을 1단계(all_vecs) fix → 전 portfolio
# 가 paper-faithful 1단계 Bernoulli 로 통일된다 (B1 mode 는 이미 1단계).
#
# 순서: [1] B1 1단계 재측정 80 → [2] CaseA 1364 → [3] CaseB 1단계 재측정 1364 → [4] K-gran 156
# 각 sub-script idempotent + 고정 출력 dir → tmux 중단/서버 재부팅 후 그대로 재실행 안전.
# 순차 = 80M sf100 NPY 동시 적재 RAM 충돌 회피.
#   사용: tmux new -d -s campaign 'bash /tmp/launch_master_campaign_5_17.sh'
set -u
B=/mnt/hdd0/home/capstone2026

echo "[$(date)] ======== MASTER CAMPAIGN v2 START ========"

echo "[$(date)] === [1/4] B1 1단계 재측정 (80) ==="
bash /tmp/launch_b1redo_5_17.sh /tmp/b1redo_tasks_5_17.txt "$B/results_b1redo_1stage"

echo "[$(date)] === [2/4] CaseA 전체 portfolio (1364) ==="
bash /tmp/launch_caseA_full_5_17.sh /tmp/caseA_tasks_5_17.txt "$B/results_caseA_full"

echo "[$(date)] === [3/4] CaseB 1단계 재측정 (1364) ==="
bash /tmp/launch_caseB_redo_5_17.sh /tmp/caseA_tasks_5_17.txt "$B/results_caseB_redo_1stage"

echo "[$(date)] === [4/4] K granularity 6 cell (156) ==="
bash /tmp/launch_k_granularity_6cell_5_17.sh "$B/results_k_granularity_6cell"

echo "[$(date)] ======== MASTER CAMPAIGN v2 DONE ========"
touch /tmp/MASTER_CAMPAIGN_DONE_5_17
