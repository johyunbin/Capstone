#!/bin/bash
# Exqutor pgvector 빌드 전용 (pg_ctl/createdb는 별도)
set -e
dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$dir"
psql_prefix="$(pwd)/psql"

# 1. 패치 적용 (2번째 실행 시 idempotent)
./apply_patch.sh || echo "apply_patch already done?"

# 2. postgres 빌드
cd "$dir/postgres"
./configure --prefix="$psql_prefix"
make -j$(nproc)
make install
cd contrib
make -j$(nproc)
make install

# 3. pgvector 빌드
cd "$dir/pgvector"
export PG_CONFIG="$psql_prefix/bin/pg_config"
make
make install

# 4. pg_hint_plan 빌드
cd "$dir/pg_hint_plan"
export PG_CONFIG="$psql_prefix/bin/pg_config"
make
make install

echo "===BUILD_CUSTOM_DONE==="
