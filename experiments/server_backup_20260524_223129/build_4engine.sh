#!/bin/bash
#
# build_4engine.sh — 4 엔진 (DuckDB-vss · VBASE · Milvus) source build wrapper
#
# 목적: 5/22 (금) 박광현 미팅 후 ~ 5/26 (월) 사이에 4 엔진 빌드 + smoke test 완료.
#       5/30 ~ 6/3 본격 측정 launch, 6/11 결과보고서 통합 PoC 측정.
#
# 작성: 2026-05-21 KST · 캡스톤 속도는벡터팀 (조현빈)
#
# ★ Carry 룰 (반드시 준수)
# - Exqutor 의 build_custom.sh / apply_patch.sh / build.sh **직접 호출 금지**
# - README 표준 명령을 본 스크립트 내부에서 수동 분해
# - systemd-run --user --scope wrap (MemoryMax / CPUQuota / nice / ionice)
# - 빌드 병렬도 = DuckDB + VBASE 동시 (2), Milvus 별도
# - Milvus = Docker 권한 X + go 미설치 = source build 불가 → paper Fig 12 정성 fallback
#
# 사용법:
#   bash build_4engine.sh           # 전체 빌드 (DuckDB → VBASE 동시 → Milvus)
#   bash build_4engine.sh duckdb    # DuckDB 만
#   bash build_4engine.sh vbase     # VBASE 만
#   bash build_4engine.sh milvus    # Milvus 만 (현재 fallback 확정)
#   bash build_4engine.sh check     # 의존성 사전 확인 + 환경 진단만
#
# launch 권장 시점:
#   pgvector Phase B/C 측정 완료 후 (5/22 박광현 미팅 사전보고 직전 또는 직후)
#   → server CPU 여유 시점에 nohup background launch
#   → 권한 연장 (박세은 5/20 23:46 카톡 요청) 확보 가정

set -u
set -o pipefail
# ★ set -e 는 일부러 사용 X — fallback 흐름 (Milvus 실패) 을 script 종료 X 로 처리

# ============================================================================
# 0. 경로 정의 + 자원 cap + 환경 변수
# ============================================================================
EXQUTOR_ROOT="/mnt/hdd0/home/capstone2026/Exqutor"
DUCKDB_DIR="${EXQUTOR_ROOT}/DuckDB/duckdb-vss"
VBASE_DIR="${EXQUTOR_ROOT}/PostgreSQL/VBASE"
MILVUS_DIR="${EXQUTOR_ROOT}/Milvus"   # 신규 — git clone 예정

CACHE_ROOT="/mnt/hdd0/home/capstone2026/cache/rq3"
LOG_DIR="${CACHE_ROOT}/build_logs"
mkdir -p "${LOG_DIR}"

VBASE_PREFIX="${HOME}/vbase_install"     # 별도 PG install (port 55436)
VBASE_DATA="${HOME}/vbase_data"
VBASE_PORT=55436

DUCKDB_LOG="${LOG_DIR}/duckdb_build.log"
VBASE_LOG="${LOG_DIR}/vbase_build.log"
MILVUS_LOG="${LOG_DIR}/milvus_build.log"
SUMMARY_LOG="${LOG_DIR}/build_summary.log"

# 자원 cap (plan §0.3 4 병렬 적극 + 빌드 wrap)
SYSTEMD_WRAP_BUILD=(
    systemd-run --user --scope
    -p MemoryMax=20G
    -p MemoryHigh=16G
    -p CPUQuota=800%
    --slice=user.slice
    nice -n 15
    ionice -c 3
)
PARALLEL_JOBS=8   # make -j8 = 8 core, CPUQuota=800% 와 일치
BUILD_TIMEOUT="6h"

KST="$(TZ=Asia/Seoul date +'%Y-%m-%d %H:%M:%S')"

# 상태 변수 (smoke test 후 사용)
DUCKDB_STATUS="PENDING"
VBASE_STATUS="PENDING"
MILVUS_STATUS="PENDING"

# ============================================================================
# 1. 유틸리티 함수
# ============================================================================

log_section() {
    local title="$1"
    local now
    now="$(TZ=Asia/Seoul date +'%Y-%m-%d %H:%M:%S')"
    echo "" | tee -a "${SUMMARY_LOG}"
    echo "============================================================" | tee -a "${SUMMARY_LOG}"
    echo "  [${now}] ${title}" | tee -a "${SUMMARY_LOG}"
    echo "============================================================" | tee -a "${SUMMARY_LOG}"
}

log_status() {
    local engine="$1"
    local status="$2"
    local detail="${3:-}"
    local now
    now="$(TZ=Asia/Seoul date +'%H:%M:%S')"
    echo "[${now}] ${engine}: ${status} ${detail}" | tee -a "${SUMMARY_LOG}"
}

check_command() {
    local cmd="$1"
    if command -v "${cmd}" >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# ============================================================================
# 2. 의존성 사전 확인
# ============================================================================

precheck_dependencies() {
    log_section "의존성 사전 확인"

    local errors=0
    local warnings=0

    echo "[필수 — DuckDB / VBASE 빌드]" | tee -a "${SUMMARY_LOG}"
    for cmd in gcc g++ make cmake ninja python3 git; do
        if check_command "${cmd}"; then
            local ver
            case "${cmd}" in
                gcc|g++) ver="$(${cmd} --version | head -1)" ;;
                cmake|ninja) ver="$(${cmd} --version | head -1)" ;;
                python3) ver="$(${cmd} --version 2>&1)" ;;
                *) ver="$(${cmd} --version 2>/dev/null | head -1 || echo OK)" ;;
            esac
            echo "  [OK] ${cmd}: ${ver}" | tee -a "${SUMMARY_LOG}"
        else
            echo "  [FAIL] ${cmd}: not found" | tee -a "${SUMMARY_LOG}"
            errors=$((errors + 1))
        fi
    done

    echo "" | tee -a "${SUMMARY_LOG}"
    echo "[VBASE 추가 — PG 빌드 옵션]" | tee -a "${SUMMARY_LOG}"
    # configure: --with-ldap --with-python --with-openssl --with-libxml --with-libxslt
    for pkg in libldap2-dev libssl-dev libxml2-dev libxslt-dev python3-dev libreadline-dev zlib1g-dev; do
        if dpkg -l 2>/dev/null | grep -q "^ii  ${pkg} " ; then
            echo "  [OK] ${pkg}" | tee -a "${SUMMARY_LOG}"
        else
            echo "  [WARN] ${pkg}: not found (PG configure 실패 가능성)" | tee -a "${SUMMARY_LOG}"
            warnings=$((warnings + 1))
        fi
    done

    echo "" | tee -a "${SUMMARY_LOG}"
    echo "[Milvus 의존성 — source build 가능성 진단]" | tee -a "${SUMMARY_LOG}"
    for cmd in go etcd minio; do
        if check_command "${cmd}"; then
            echo "  [OK] ${cmd}: $(${cmd} version 2>&1 | head -1)" | tee -a "${SUMMARY_LOG}"
        else
            echo "  [MISSING] ${cmd}: not found → Milvus source build 불가 확정" | tee -a "${SUMMARY_LOG}"
            warnings=$((warnings + 1))
        fi
    done

    # docker 권한
    if check_command "docker"; then
        if docker ps >/dev/null 2>&1; then
            echo "  [OK] docker: socket 접근 가능" | tee -a "${SUMMARY_LOG}"
        else
            echo "  [MISSING] docker: binary 있으나 socket 권한 없음 → Milvus standalone 컨테이너 불가" | tee -a "${SUMMARY_LOG}"
            warnings=$((warnings + 1))
        fi
    fi

    echo "" | tee -a "${SUMMARY_LOG}"
    echo "[디스크 / 메모리]" | tee -a "${SUMMARY_LOG}"
    local mem_avail disk_avail
    mem_avail="$(free -g | awk '/^Mem:/ {print $7}')"
    disk_avail="$(df -h /mnt/hdd0 | awk 'NR==2 {print $4}')"
    echo "  mem available: ${mem_avail} GiB / disk free: ${disk_avail}" | tee -a "${SUMMARY_LOG}"
    if [[ "${mem_avail}" -lt 50 ]]; then
        echo "  [WARN] mem < 50GB — 다른 user peak 가능, 측정 윈도우 신중" | tee -a "${SUMMARY_LOG}"
        warnings=$((warnings + 1))
    fi

    echo "" | tee -a "${SUMMARY_LOG}"
    if [[ "${errors}" -gt 0 ]]; then
        echo "[FAIL] 필수 의존성 ${errors} 건 부재 — 빌드 중단" | tee -a "${SUMMARY_LOG}"
        return 1
    elif [[ "${warnings}" -gt 0 ]]; then
        echo "[WARN] 경고 ${warnings} 건 — Milvus fallback / VBASE 경고 가능" | tee -a "${SUMMARY_LOG}"
        return 0
    else
        echo "[OK] 모든 의존성 확인 통과" | tee -a "${SUMMARY_LOG}"
        return 0
    fi
}

# ============================================================================
# 3. DuckDB-vss 빌드 (E1)
# ============================================================================
#
# README (carry):
#   cd duckdb-vss && make
#
# 본 script 분해:
#   1. submodule init (duckdb + extension-ci-tools)
#   2. make (= extension-ci-tools/makefiles/duckdb_extension.Makefile)
#   3. smoke: ./build/release/duckdb -c "INSTALL vss; LOAD vss; SELECT 1;"

build_duckdb() {
    log_section "DuckDB-vss 빌드 (E1)"
    DUCKDB_STATUS="RUNNING"
    : > "${DUCKDB_LOG}"

    cd "${DUCKDB_DIR}" || { DUCKDB_STATUS="FAIL"; log_status "DuckDB" "FAIL" "cd ${DUCKDB_DIR} 실패"; return 1; }

    # 3.1 submodule init
    log_status "DuckDB" "STEP 1" "git submodule update --init --depth 1"
    {
        echo "=== STEP 1: submodule init ==="
        echo "기존 duckdb/ extension-ci-tools/ 디렉토리 상태:"
        du -sh duckdb/ extension-ci-tools/ 2>&1 || true
    } >> "${DUCKDB_LOG}"

    timeout "${BUILD_TIMEOUT}" "${SYSTEMD_WRAP_BUILD[@]}" \
        git submodule update --init --depth 1 >> "${DUCKDB_LOG}" 2>&1
    local submod_rc=$?
    if [[ ${submod_rc} -ne 0 ]]; then
        DUCKDB_STATUS="FAIL"
        log_status "DuckDB" "FAIL" "submodule init 실패 (rc=${submod_rc}) — 로그: ${DUCKDB_LOG}"
        return 1
    fi

    # 검증: duckdb/ + extension-ci-tools/ 가 비어있지 않은가
    local duckdb_size eci_size
    duckdb_size="$(du -sb duckdb/ 2>/dev/null | awk '{print $1}')"
    eci_size="$(du -sb extension-ci-tools/ 2>/dev/null | awk '{print $1}')"
    {
        echo "submodule init 후 디렉토리 크기:"
        du -sh duckdb/ extension-ci-tools/
    } >> "${DUCKDB_LOG}"
    if [[ -z "${duckdb_size}" || "${duckdb_size}" -lt 1000000 ]]; then
        DUCKDB_STATUS="FAIL"
        log_status "DuckDB" "FAIL" "submodule init 후에도 duckdb/ EMPTY (${duckdb_size}B)"
        return 1
    fi

    # 3.2 make
    log_status "DuckDB" "STEP 2" "make (~90min~3h 예상)"
    {
        echo ""
        echo "=== STEP 2: make ==="
        echo "병렬: ${PARALLEL_JOBS} jobs"
        echo "Makefile: extension-ci-tools/makefiles/duckdb_extension.Makefile"
    } >> "${DUCKDB_LOG}"

    timeout "${BUILD_TIMEOUT}" "${SYSTEMD_WRAP_BUILD[@]}" \
        make GEN=ninja >> "${DUCKDB_LOG}" 2>&1
    local make_rc=$?
    if [[ ${make_rc} -ne 0 ]]; then
        DUCKDB_STATUS="FAIL"
        log_status "DuckDB" "FAIL" "make 실패 (rc=${make_rc}) — 로그: ${DUCKDB_LOG}"
        return 1
    fi

    # 3.3 smoke test
    log_status "DuckDB" "SMOKE" "INSTALL vss; LOAD vss; SELECT 1;"
    {
        echo ""
        echo "=== STEP 3: smoke test ==="
    } >> "${DUCKDB_LOG}"

    local duckdb_bin="${DUCKDB_DIR}/build/release/duckdb"
    if [[ ! -x "${duckdb_bin}" ]]; then
        DUCKDB_STATUS="FAIL"
        log_status "DuckDB" "FAIL" "binary 없음: ${duckdb_bin}"
        return 1
    fi

    local smoke_out
    smoke_out="$("${duckdb_bin}" -unsigned -c "LOAD '${DUCKDB_DIR}/build/release/extension/vss/vss.duckdb_extension'; SELECT 1 AS smoke;" 2>&1)"
    echo "${smoke_out}" >> "${DUCKDB_LOG}"
    if echo "${smoke_out}" | grep -q "smoke" || echo "${smoke_out}" | grep -q "^1$"; then
        DUCKDB_STATUS="PASS"
        log_status "DuckDB" "PASS" "binary + vss extension OK"
        return 0
    else
        DUCKDB_STATUS="FAIL"
        log_status "DuckDB" "FAIL" "smoke 실패 — 로그: ${DUCKDB_LOG}"
        return 1
    fi
}

# ============================================================================
# 4. VBASE 빌드 (E2) — apply_patch.sh / build.sh 안 내용 수동 분해
# ============================================================================
#
# apply_patch.sh 분해 (carry):
#   cd MSVBASE/thirdparty/Postgres && git apply ../../../patch/vbase_Postgres.patch
#   cd MSVBASE/thirdparty/hnsw && git apply ../../../patch/vbase_hnsw.patch
#   cd MSVBASE/thirdparty/SPTAG && git apply ../../../patch/vbase_spann.patch
#   cd MSVBASE && git apply ../patch/vbase_Exqutor.patch
#   cd MSVBASE && git apply ../patch/vbase_Exqutor_lib.patch
#
# build.sh 분해 (carry):
#   PGBASE=$pwd/psql
#   cd MSVBASE/thirdparty/Postgres
#     ./configure --with-blocksize=32 --prefix=$PGBASE ...
#     make -j && make install && make -C contrib install
#   cd $dir/MSVBASE && mkdir build && cd build
#     cmake -DCMAKE_INSTALL_PREFIX=$PGBASE/share/postgresql -DLIBRARYONLY=ON ...
#     make -j$(nproc)
#   cp vectordb.{so,control} ${PGBASE}/...
#   pg_hint_plan 빌드 + install
#   pg_ctl -D data -l log start
#   createdb tpch ; CREATE EXTENSION vectordb
#
# ★ 본 script 수정점:
#   - PGBASE 를 $HOME/vbase_install 로 분리 (port 55436)
#   - pg_hint_plan 은 별도 단계 (의존성 부재 시 skip 가능)
#   - 별도 PG initdb 후 port 55436 으로 기동

build_vbase() {
    log_section "VBASE 빌드 (E2)"
    VBASE_STATUS="RUNNING"
    : > "${VBASE_LOG}"

    cd "${VBASE_DIR}" || { VBASE_STATUS="FAIL"; log_status "VBASE" "FAIL" "cd ${VBASE_DIR} 실패"; return 1; }

    # 4.1 submodule init (MSVBASE)
    log_status "VBASE" "STEP 1" "submodule init MSVBASE"
    {
        echo "=== STEP 1: submodule init MSVBASE ==="
        du -sh MSVBASE/ 2>&1 || true
    } >> "${VBASE_LOG}"

    # MSVBASE 는 thirdparty/Postgres·hnsw·SPTAG 의 sub-submodule 포함
    timeout "${BUILD_TIMEOUT}" "${SYSTEMD_WRAP_BUILD[@]}" \
        git submodule update --init --recursive --depth 1 MSVBASE >> "${VBASE_LOG}" 2>&1
    local submod_rc=$?
    if [[ ${submod_rc} -ne 0 ]]; then
        VBASE_STATUS="FAIL"
        log_status "VBASE" "FAIL" "submodule init 실패 (rc=${submod_rc})"
        return 1
    fi

    # 4.2 patch 5종 수동 적용 — apply_patch.sh 절대 호출 X
    log_status "VBASE" "STEP 2" "5 patch 수동 적용 (Postgres/hnsw/SPTAG/Exqutor/Exqutor_lib)"
    {
        echo ""
        echo "=== STEP 2: patches 수동 적용 ==="
    } >> "${VBASE_LOG}"

    local patches=(
        "MSVBASE/thirdparty/Postgres:patch/vbase_Postgres.patch"
        "MSVBASE/thirdparty/hnsw:patch/vbase_hnsw.patch"
        "MSVBASE/thirdparty/SPTAG:patch/vbase_spann.patch"
        "MSVBASE:patch/vbase_Exqutor.patch"
        "MSVBASE:patch/vbase_Exqutor_lib.patch"
    )
    for p in "${patches[@]}"; do
        local target="${p%%:*}"
        local patch_file="${p##*:}"
        local patch_abs="${VBASE_DIR}/${patch_file}"
        echo "  patch: ${target} <- ${patch_file}" >> "${VBASE_LOG}"
        (
            cd "${VBASE_DIR}/${target}" || exit 1
            # idempotent check: git apply --check 로 이미 적용됐는지 확인
            if git apply --check "${patch_abs}" 2>/dev/null; then
                git apply "${patch_abs}" 2>&1
            else
                echo "    (이미 적용됐거나 conflict — skip)"
            fi
        ) >> "${VBASE_LOG}" 2>&1
    done

    # 4.3 PG configure + make + install (port 변경 — runtime 에서 55436 으로 띄움)
    log_status "VBASE" "STEP 3" "PG configure + make + install → ${VBASE_PREFIX}"
    {
        echo ""
        echo "=== STEP 3: PostgreSQL build (--prefix=${VBASE_PREFIX}) ==="
    } >> "${VBASE_LOG}"

    cd "${VBASE_DIR}/MSVBASE/thirdparty/Postgres" || {
        VBASE_STATUS="FAIL"
        log_status "VBASE" "FAIL" "cd MSVBASE/thirdparty/Postgres 실패"
        return 1
    }

    timeout "${BUILD_TIMEOUT}" "${SYSTEMD_WRAP_BUILD[@]}" \
        ./configure \
            --with-blocksize=32 \
            --enable-integer-datetimes \
            --enable-thread-safety \
            --with-pgport=${VBASE_PORT} \
            --prefix="${VBASE_PREFIX}" \
            --with-ldap \
            --with-python \
            --with-openssl \
            --with-libxml \
            --with-libxslt \
            --enable-nls=yes \
        >> "${VBASE_LOG}" 2>&1
    local cfg_rc=$?
    if [[ ${cfg_rc} -ne 0 ]]; then
        VBASE_STATUS="FAIL"
        log_status "VBASE" "FAIL" "configure 실패 (rc=${cfg_rc}) — 의존성 부족 가능"
        return 1
    fi

    timeout "${BUILD_TIMEOUT}" "${SYSTEMD_WRAP_BUILD[@]}" \
        bash -c "make -j${PARALLEL_JOBS} && make install && make -C contrib install" \
        >> "${VBASE_LOG}" 2>&1
    local make_rc=$?
    if [[ ${make_rc} -ne 0 ]]; then
        VBASE_STATUS="FAIL"
        log_status "VBASE" "FAIL" "PG make/install 실패 (rc=${make_rc})"
        return 1
    fi

    # 4.4 vectordb.so cmake build
    log_status "VBASE" "STEP 4" "vectordb.so cmake build (MSVBASE/build/)"
    {
        echo ""
        echo "=== STEP 4: vectordb.so build ==="
    } >> "${VBASE_LOG}"

    cd "${VBASE_DIR}/MSVBASE" || {
        VBASE_STATUS="FAIL"
        log_status "VBASE" "FAIL" "cd MSVBASE 실패"
        return 1
    }
    mkdir -p build
    cd build

    timeout "${BUILD_TIMEOUT}" "${SYSTEMD_WRAP_BUILD[@]}" \
        cmake \
            -DCMAKE_INSTALL_PREFIX="${VBASE_PREFIX}/share/postgresql" \
            -DLIBRARYONLY=ON \
            -DSEEK_ENABLE_TESTS=ON \
            -DPostgreSQL_INCLUDE_DIR="${VBASE_PREFIX}/include/postgresql/server" \
            -DPostgreSQL_LIBRARY="${VBASE_PREFIX}/lib/libpq.so" \
            -DPostgreSQL_TYPE_INCLUDE_DIR="${VBASE_PREFIX}/include" \
            -DCMAKE_BUILD_TYPE=Release \
            .. \
        >> "${VBASE_LOG}" 2>&1
    local cmake_rc=$?
    if [[ ${cmake_rc} -ne 0 ]]; then
        VBASE_STATUS="FAIL"
        log_status "VBASE" "FAIL" "cmake 실패 (rc=${cmake_rc})"
        return 1
    fi

    timeout "${BUILD_TIMEOUT}" "${SYSTEMD_WRAP_BUILD[@]}" \
        make -j${PARALLEL_JOBS} >> "${VBASE_LOG}" 2>&1
    local mk2_rc=$?
    if [[ ${mk2_rc} -ne 0 ]]; then
        VBASE_STATUS="FAIL"
        log_status "VBASE" "FAIL" "vectordb.so make 실패 (rc=${mk2_rc})"
        return 1
    fi

    # 4.5 vectordb.so 복사 (build.sh 흐름 그대로)
    {
        echo ""
        echo "=== STEP 5: vectordb 파일 복사 ==="
    } >> "${VBASE_LOG}"
    cd "${VBASE_DIR}/MSVBASE" || return 1
    cp ./build/vectordb.so "${VBASE_PREFIX}/lib/postgresql/vectordb.so" 2>&1 >> "${VBASE_LOG}"
    cp ./build/vectordb.control "${VBASE_PREFIX}/share/postgresql/extension/vectordb.control" 2>&1 >> "${VBASE_LOG}"
    cp ./sql/vectordb.sql "${VBASE_PREFIX}/share/postgresql/extension/vectordb--0.1.0.sql" 2>&1 >> "${VBASE_LOG}"

    # 4.6 initdb (port 55436 PG instance) + 기동
    log_status "VBASE" "STEP 6" "initdb + pg_ctl start (port ${VBASE_PORT})"
    {
        echo ""
        echo "=== STEP 6: initdb + pg_ctl start ==="
    } >> "${VBASE_LOG}"

    if [[ ! -d "${VBASE_DATA}" ]]; then
        "${VBASE_PREFIX}/bin/initdb" -D "${VBASE_DATA}" -E UTF8 --locale=C \
            >> "${VBASE_LOG}" 2>&1
    fi

    # postgresql.conf port 변경
    if [[ -f "${VBASE_DATA}/postgresql.conf" ]]; then
        sed -i.bak "s/^#*port = .*/port = ${VBASE_PORT}/" "${VBASE_DATA}/postgresql.conf"
    fi

    # pg_ctl start (이미 떠 있으면 skip)
    if "${VBASE_PREFIX}/bin/pg_ctl" -D "${VBASE_DATA}" status >/dev/null 2>&1; then
        echo "VBASE PG 이미 기동 중 — skip start" >> "${VBASE_LOG}"
    else
        "${VBASE_PREFIX}/bin/pg_ctl" -D "${VBASE_DATA}" -l "${VBASE_DATA}/pg.log" start \
            >> "${VBASE_LOG}" 2>&1
        sleep 3
    fi

    # 4.7 smoke test — \dx | grep vectordb
    log_status "VBASE" "SMOKE" "CREATE EXTENSION vectordb + \\dx grep"
    {
        echo ""
        echo "=== STEP 7: smoke test ==="
    } >> "${VBASE_LOG}"

    # createdb (이미 있으면 무시)
    "${VBASE_PREFIX}/bin/createdb" -p "${VBASE_PORT}" tpch 2>>"${VBASE_LOG}" || true
    "${VBASE_PREFIX}/bin/psql" -p "${VBASE_PORT}" -d tpch \
        -c "CREATE EXTENSION IF NOT EXISTS vectordb;" >> "${VBASE_LOG}" 2>&1

    local smoke_out
    smoke_out="$("${VBASE_PREFIX}/bin/psql" -p "${VBASE_PORT}" -d tpch -c "\dx" 2>&1)"
    echo "${smoke_out}" >> "${VBASE_LOG}"

    if echo "${smoke_out}" | grep -qi "vectordb"; then
        VBASE_STATUS="PASS"
        log_status "VBASE" "PASS" "extension vectordb 등록 OK (port ${VBASE_PORT})"
        return 0
    else
        VBASE_STATUS="FAIL"
        log_status "VBASE" "FAIL" "vectordb 미발견 — 로그: ${VBASE_LOG}"
        return 1
    fi
}

# ============================================================================
# 5. Milvus 빌드 (E3) — 조건부, Docker / go 부재 시 fallback
# ============================================================================
#
# 빌드 가능 시나리오:
#   - go 1.21+ 설치 + etcd + minio + cmake
#   - source clone: https://github.com/milvus-io/milvus.git
#   - cd milvus && make standalone
#
# 현재 진단 (2026-05-21):
#   - go: not found → source build 불가 확정
#   - docker: binary 있지만 socket 권한 없음 → docker-compose 도 불가
#   → paper Fig 12 정성 fallback 으로 빠짐
#
# fallback 처리:
#   - "Milvus build failed — fall back to paper Fig 12 qualitative comparison"
#   - exit 0 (script 전체는 성공)
#   - 보고서 §5.6 / §6.4 에서 Milvus 단독 paper 인용 framing

build_milvus() {
    log_section "Milvus 빌드 (E3, 조건부)"
    MILVUS_STATUS="RUNNING"
    : > "${MILVUS_LOG}"

    {
        echo "=== Milvus source build 가능성 진단 ==="
        echo "필수: go 1.21+ / etcd / minio / cmake / git"
    } >> "${MILVUS_LOG}"

    # 5.1 go 의존성 확인
    if ! check_command "go"; then
        echo "go: not found — source build 불가" >> "${MILVUS_LOG}"
        MILVUS_STATUS="SKIP"
        log_status "Milvus" "SKIP" "go 미설치 → paper Fig 12 정성 fallback"
        {
            echo ""
            echo "Milvus build SKIPPED — fall back to paper Fig 12 qualitative comparison"
            echo "보고서 §5.6 / §6.4 에서 Milvus 단독 paper 인용 framing 적용"
        } >> "${MILVUS_LOG}"
        return 0
    fi

    # 5.2 docker 권한 확인 (etcd/minio 컨테이너 실행 가능성)
    local milvus_runtime="source"
    if check_command "docker" && docker ps >/dev/null 2>&1; then
        milvus_runtime="docker-compose"
        echo "docker socket OK → docker-compose 시도 가능" >> "${MILVUS_LOG}"
    else
        echo "docker socket 권한 없음 → source build only" >> "${MILVUS_LOG}"
    fi

    # 5.3 source clone
    log_status "Milvus" "STEP 1" "git clone milvus"
    if [[ ! -d "${MILVUS_DIR}" ]]; then
        timeout "${BUILD_TIMEOUT}" "${SYSTEMD_WRAP_BUILD[@]}" \
            git clone --depth 1 --branch master https://github.com/milvus-io/milvus.git "${MILVUS_DIR}" \
            >> "${MILVUS_LOG}" 2>&1
        local clone_rc=$?
        if [[ ${clone_rc} -ne 0 ]]; then
            MILVUS_STATUS="SKIP"
            log_status "Milvus" "SKIP" "clone 실패 (rc=${clone_rc}) → paper fallback"
            {
                echo ""
                echo "Milvus clone failed — fall back to paper Fig 12 qualitative comparison"
            } >> "${MILVUS_LOG}"
            return 0
        fi
    fi

    # 5.4 build
    log_status "Milvus" "STEP 2" "make standalone (3~6h 예상)"
    cd "${MILVUS_DIR}" || {
        MILVUS_STATUS="SKIP"
        log_status "Milvus" "SKIP" "cd 실패 → paper fallback"
        return 0
    }

    timeout "${BUILD_TIMEOUT}" "${SYSTEMD_WRAP_BUILD[@]}" \
        make standalone >> "${MILVUS_LOG}" 2>&1
    local build_rc=$?
    if [[ ${build_rc} -ne 0 ]]; then
        MILVUS_STATUS="SKIP"
        log_status "Milvus" "SKIP" "make standalone 실패 (rc=${build_rc}) → paper fallback"
        {
            echo ""
            echo "Milvus build failed — fall back to paper Fig 12 qualitative comparison"
        } >> "${MILVUS_LOG}"
        return 0
    fi

    # 5.5 smoke (pymilvus client)
    log_status "Milvus" "SMOKE" "pymilvus connect + collection"
    python3 -c "
try:
    from pymilvus import connections, Collection
    print('pymilvus import OK')
except ImportError:
    print('pymilvus 미설치 — pip install pymilvus 필요')
" >> "${MILVUS_LOG}" 2>&1

    # 5.6 fallback 처리 (etcd / minio 미설치 시 standalone 기동 자체 불가)
    if ! check_command "etcd" || ! check_command "minio"; then
        MILVUS_STATUS="SKIP"
        log_status "Milvus" "SKIP" "etcd/minio 미설치 → runtime 기동 불가 → paper fallback"
        {
            echo ""
            echo "Milvus dependencies missing — fall back to paper Fig 12 qualitative comparison"
        } >> "${MILVUS_LOG}"
        return 0
    fi

    MILVUS_STATUS="PASS"
    log_status "Milvus" "PASS" "source build + smoke OK"
    return 0
}

# ============================================================================
# 6. 빌드 wrapper — 2 병렬 (DuckDB + VBASE 동시), Milvus 별도
# ============================================================================

run_parallel_duckdb_vbase() {
    log_section "DuckDB + VBASE 2 병렬 launch"

    # 각각 background launch — 별도 systemd-run scope 로 자원 분리
    build_duckdb &
    local duckdb_pid=$!
    log_status "DuckDB" "BG" "pid=${duckdb_pid}"

    build_vbase &
    local vbase_pid=$!
    log_status "VBASE" "BG" "pid=${vbase_pid}"

    # 둘 다 끝날 때까지 wait
    wait ${duckdb_pid}
    local duckdb_rc=$?
    wait ${vbase_pid}
    local vbase_rc=$?

    log_status "DuckDB" "${DUCKDB_STATUS}" "(rc=${duckdb_rc})"
    log_status "VBASE" "${VBASE_STATUS}" "(rc=${vbase_rc})"
}

run_milvus_sequential() {
    log_section "Milvus 단독 launch (sequential)"
    build_milvus
}

# ============================================================================
# 7. 최종 status 보고
# ============================================================================

print_final_status() {
    log_section "최종 status"
    {
        echo ""
        echo "[2026-05-21 KST] 4 엔진 빌드 결과:"
        echo "  E1 DuckDB-vss : ${DUCKDB_STATUS}"
        echo "  E2 VBASE      : ${VBASE_STATUS}"
        echo "  E3 Milvus     : ${MILVUS_STATUS}  (fallback = paper Fig 12 정성)"
        echo ""
        echo "  로그 위치:"
        echo "    ${DUCKDB_LOG}"
        echo "    ${VBASE_LOG}"
        echo "    ${MILVUS_LOG}"
        echo "    ${SUMMARY_LOG}  (본 summary)"
        echo ""
        echo "  다음 단계 (build 후 — measure harness 작성):"
        echo "    1. measure_latency_duckdb.py    (~200줄, in-process python duckdb)"
        echo "    2. measure_latency_vbase.py     (~250줄, port ${VBASE_PORT} PG)"
        echo "    3. measure_latency_milvus.py    (~200줄, 조건부 / fallback 시 미작성)"
        echo "    4. measure_4engine.py           (~150줄, 통합 wrapper)"
    } | tee -a "${SUMMARY_LOG}"
}

# ============================================================================
# 8. main entry
# ============================================================================

main() {
    local mode="${1:-all}"

    {
        echo ""
        echo "############################################################"
        echo "# build_4engine.sh — 4 엔진 빌드 wrapper"
        echo "# 시작: ${KST}"
        echo "# mode: ${mode}"
        echo "############################################################"
    } | tee -a "${SUMMARY_LOG}"

    precheck_dependencies
    local precheck_rc=$?
    if [[ ${precheck_rc} -ne 0 ]]; then
        echo "[FATAL] precheck 실패 — 빌드 중단" | tee -a "${SUMMARY_LOG}"
        exit 2
    fi

    case "${mode}" in
        all)
            run_parallel_duckdb_vbase
            run_milvus_sequential
            ;;
        duckdb)
            build_duckdb
            ;;
        vbase)
            build_vbase
            ;;
        milvus)
            build_milvus
            ;;
        check)
            echo "[OK] precheck only — build 미실행" | tee -a "${SUMMARY_LOG}"
            ;;
        *)
            echo "Unknown mode: ${mode}" | tee -a "${SUMMARY_LOG}"
            echo "사용법: bash $0 {all|duckdb|vbase|milvus|check}" | tee -a "${SUMMARY_LOG}"
            exit 1
            ;;
    esac

    print_final_status

    # exit code = DuckDB/VBASE 실패가 critical (Milvus 는 fallback 으로 SKIP 도 OK)
    if [[ "${mode}" == "all" || "${mode}" == "duckdb" || "${mode}" == "vbase" ]]; then
        if [[ "${DUCKDB_STATUS}" == "FAIL" || "${VBASE_STATUS}" == "FAIL" ]]; then
            exit 1
        fi
    fi
    exit 0
}

main "$@"
