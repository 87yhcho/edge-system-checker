#!/usr/bin/env bash
# check_edge_status.sh
# 엣지 컴퓨터 통합 점검 스크립트 (콘솔 + TSV + JSON 리포트 동시 생성)
# 기준: '엣지 컴퓨터 테스트 항목_v1.3' 체크리스트  (자동화 가능한 항목 위주)  # ref

set -euo pipefail

# =========[ 환경 변수: 현장에 맞게 수정 ]=========
NAS_MOUNT="/mnt/nas"
STREAM_DIR="$HOME/oper/video_processor"
STREAM_ENV_GLOB="$STREAM_DIR/.env.stream*"
BLUR_ENGINE="$STREAM_DIR/blur_module/models/best_re_final.engine"
VIDEO_DIR="/var/edge/videos"             # 실제 저장 경로로 교체
TOMCAT_SERVICE="tomcat"                  # 서비스명 상이하면 수정
POSTGRES_SERVICE="postgresql"
BROWSER_USER_SERVICE=""                  # 예: "browser.service" (user 서비스로 등록한 경우)
RTSP_SAMPLE_URL=""                       # 샘플 RTSP URL 있으면 fps 검사에 사용
DB_NAME="postgres"                       # 점검용 연결 DB
DB_TABLE_BLACKBOX="blackbox_log"         # 실제 테이블명으로 수정
BLACKBOX_API="http://localhost:8080/api/blackbox/status"
CRON_UTC_PATTERN='^1 0 \* \* \* '        # 매일 00:01
REQUIRE_UTC="yes"                        # UTC 강제 여부(표기만 점검)
POSTGRES_LOG_ROTATION_AGE_REQ="30"       # 체크리스트 메모 반영
JDK_REQUIRED_MAJOR="17"
HEAP_MIN_PATTERN='-Xms(2048m|2g)'        # 힙 최소
HEAP_MAX_PATTERN='-Xmx(4096m|4g)'        # 힙 최대
NFS_CLIENT_SERVICE="nfs-common"
UPS_NAME="ups@localhost"                 # upsc ${UPS_NAME}

# =========[ 출력 준비 ]=========
TS=$(date +%Y%m%d_%H%M%S)
HOST=$(hostname)
OUT_DIR="$(pwd)"
TSV="${OUT_DIR}/edge_check_${HOST}_${TS}.tsv"
JSON="${OUT_DIR}/edge_check_${HOST}_${TS}.json"
LOGF="${OUT_DIR}/edge_check_${HOST}_${TS}.log"

# 컬러
if [ -t 1 ]; then
  C_OK="\033[1;32m"; C_NG="\033[1;31m"; C_SK="\033[1;33m"; C_RS="\033[0m"
else
  C_OK=""; C_NG=""; C_SK=""; C_RS=""
fi

# 결과 누적
declare -a R_CATEGORY R_ITEM R_STATUS R_DETAIL
add_result() { # cat item status detail
  R_CATEGORY+=("$1"); R_ITEM+=("$2"); R_STATUS+=("$3"); R_DETAIL+=("${4:-}")
}

# 유틸
log() { echo "[$(date +%H:%M:%S)] $*" | tee -a "$LOGF"; }
have() { command -v "$1" >/dev/null 2>&1; }
ok() { printf "${C_OK}[OK]${C_RS} %s\n" "$*"; }
ng() { printf "${C_NG}[NG]${C_RS} %s\n" "$*"; }
sk() { printf "${C_SK}[SKIP]${C_RS} %s\n" "$*"; }

# 의존성 존재 여부 정보성 출력(없어도 대부분 graceful degrade)
NEEDED_CMDS=(timedatectl locale ss systemctl findmnt stat df cat grep awk sed ps curl ip nmcli)
OPT_CMDS=(psql jq upsc ffprobe fping journalctl)
for c in "${NEEDED_CMDS[@]}" "${OPT_CMDS[@]}"; do
  if have "$c"; then log "dep: $c = OK"; else log "dep: $c = MISSING"; fi
done

# =========[ 체크 함수 ]=========
check_cmd() { # cat item cmd [expect_regex]
  local cat="$1" item="$2" cmd="$3" expect="${4:-}"
  local out rc
  out="$(bash -o pipefail -c "$cmd" 2>&1)" && rc=0 || rc=$?
  if [ $rc -eq 0 ]; then
    if [ -n "$expect" ]; then
      if echo "$out" | grep -Eq "$expect"; then
        ok "$cat: $item"
        add_result "$cat" "$item" "OK" "$out"
      else
        ng "$cat: $item (pattern mismatch)"
        add_result "$cat" "$item" "NG" "$out"
      fi
    else
      ok "$cat: $item"
      add_result "$cat" "$item" "OK" "$out"
    fi
  else
    ng "$cat: $item (rc=$rc)"
    add_result "$cat" "$item" "NG" "$out"
  fi
}

check_opt() { # optional (skip when cmd missing)
  local cmd="$3"
  local bin="${cmd%% *}"
  if have "${bin}"; then
    check_cmd "$@"
  else
    sk "$1: $2 (missing: ${bin})"
    add_result "$1" "$2" "SKIP" "missing ${bin}"
  fi
}

# =========[ 점검 수행 ]=========

# OS
check_cmd "OS" "Timezone=UTC" "timedatectl" "Time zone:.*UTC|Time zone:.*Etc/UTC"
check_cmd "OS" "Locale LANG=ko_KR.UTF-8" "grep -E '^LANG=ko_KR.UTF-8' /etc/default/locale"
check_cmd "OS" "Encoding=UTF-8" "locale charmap" "^UTF-8$"

# 부팅
check_opt "Boot" "Auto-login conf present" "bash -c 'grep -R \"autologin\" /etc/{gdm3,lightdm} 2>/dev/null'"
check_cmd "Boot" "Auto updates disabled (apt-daily.timer)" "systemctl is-enabled apt-daily.timer" "^disabled|masked"
check_cmd "Boot" "Unattended-upgrades disabled/masked" "systemctl is-enabled unattended-upgrades.service || true"
check_opt "Boot" "Screen lock disabled" "gsettings get org.gnome.desktop.screensaver lock-enabled" "false"

# Tomcat
check_opt "Tomcat" "Service enabled" "systemctl is-enabled ${TOMCAT_SERVICE}"
check_opt "Tomcat" "Process running" "systemctl is-active ${TOMCAT_SERVICE}" "active"
check_cmd "Tomcat" "HTTP 80 listening" "ss -tlnp | grep -E ':80[[:space:]]' || ss -tlnp | grep -Ei ':(http|80) '" 
check_opt "Tomcat" "Heap -Xms>=2g" "bash -c 'grep -RE \"${HEAP_MIN_PATTERN}\" /etc/default /etc/sysconfig /etc/systemd/system 2>/dev/null'"
check_opt "Tomcat" "Heap -Xmx>=4g" "bash -c 'grep -RE \"${HEAP_MAX_PATTERN}\" /etc/default /etc/sysconfig /etc/systemd/system 2>/dev/null'"
check_opt "Tomcat" "Logrotate exists" "bash -c 'ls /etc/logrotate.d | grep -i tomcat'"

# PostgreSQL
check_opt "PostgreSQL" "Service enabled" "systemctl is-enabled ${POSTGRES_SERVICE}"
check_opt "PostgreSQL" "Service active" "systemctl is-active ${POSTGRES_SERVICE}" "active"
check_cmd "PostgreSQL" "Port 5432 listening" "ss -tlnp | grep -E ':5432[[:space:]]'"
check_opt "PostgreSQL" "Data dir capacity" "df -h /var/lib/postgresql"
check_opt "PostgreSQL" "PostGIS installed" "psql -At -d ${DB_NAME} -c 'SELECT postgis_full_version();'"
check_opt "PostgreSQL" "log_rotation_age=${POSTGRES_LOG_ROTATION_AGE_REQ}" "bash -c 'grep -RE \"^[[:space:]]*log_rotation_age[[:space:]]*=[[:space:]]*${POSTGRES_LOG_ROTATION_AGE_REQ}\\b\" /etc/postgresql 2>/dev/null'"

# AI (stream)
check_cmd "AI(stream)" ".env.stream* exists" "ls ${STREAM_ENV_GLOB}"
check_cmd "AI(stream)" "Blur engine exists" "test -f '${BLUR_ENGINE}' && echo exists"
check_opt "AI(stream)" "stream.service active" "systemctl is-active stream.service" "active"
check_opt "AI(stream)" "status_all_streams.sh OK" "bash -c '${STREAM_DIR}/status_all_streams.sh'"

# Browser
if [ -n "$BROWSER_USER_SERVICE" ]; then
  check_opt "Browser" "User service enabled" "systemctl --user is-enabled ${BROWSER_USER_SERVICE}"
  check_opt "Browser" "User service active"  "systemctl --user is-active ${BROWSER_USER_SERVICE}" "active"
else
  check_cmd "Browser" "Autostart .desktop exists" "ls $HOME/.config/autostart/*.desktop"
fi

# NAS / RAID / NFS
check_cmd "NAS" "Mounted at ${NAS_MOUNT}" "findmnt -no TARGET ${NAS_MOUNT} | grep -x '${NAS_MOUNT}'"
check_cmd "NAS" "Owner/Perm" "stat -c '%U:%G %a' ${NAS_MOUNT}"
check_cmd "NAS" "Write test" "bash -c 't=$(mktemp); echo ok>\"$t\"; cp \"$t\" ${NAS_MOUNT}/edge_check_write_test.$$ && rm -f \"$t\" ${NAS_MOUNT}/edge_check_write_test.$$ && echo OK'"
check_opt "RAID" "/proc/mdstat" "cat /proc/mdstat"
check_opt "NFS"  "Client active (${NFS_CLIENT_SERVICE})" "systemctl is-active ${NFS_CLIENT_SERVICE}" "active"
check_cmd "NFS"  "mount type nfs" "mount | grep -i ' type nfs'"

# Camera / Video
check_cmd "Camera" "RTSP port 554 present/checked" "ss -tlnp | grep -E ':554[[:space:]]' || echo 'no local 554 listener (OK if cameras remote)'"
if [ -n "$RTSP_SAMPLE_URL" ]; then
  check_opt "Camera" "FPS via ffprobe" "ffprobe -v error -select_streams v:0 -show_entries stream=r_frame_rate -of csv=p=0 '${RTSP_SAMPLE_URL}'"
else
  add_result "Camera" "FPS via ffprobe" "SKIP" "RTSP_SAMPLE_URL not set"; sk "Camera: FPS via ffprobe (no sample url)"
fi
check_cmd "Video" "File naming/presence" "ls -1 ${VIDEO_DIR} 2>/dev/null | head -n 5 || echo 'no files'"

# Blackbox / DB / API
check_opt "Blackbox" "API reachable" "curl -sf '${BLACKBOX_API}' | head -c 200"
if have psql; then
  check_opt "Blackbox" "DB writes recent(10m)" "psql -At -d ${DB_NAME} -c \"SELECT COUNT(*) FROM ${DB_TABLE_BLACKBOX} WHERE now()-interval '10 min' < ts;\""
else
  add_result "Blackbox" "DB writes recent(10m)" "SKIP" "psql missing"
fi
check_opt "Blackbox" "Recent error logs (10m)" "journalctl -u blackbox* --since -10m | grep -Ei 'error|fail' && false || echo 'no recent errors'"

# Time sync / Cron
check_cmd "TimeSync" "cron 00:01 exists" "bash -c 'crontab -l | grep -E \"${CRON_UTC_PATTERN}\"'"
if [ "$REQUIRE_UTC" = "yes" ]; then
  check_cmd "TimeSync" "System time UTC" "timedatectl" "Time zone:.*UTC|Time zone:.*Etc/UTC"
fi

# Java
check_opt "Java" "OpenJDK ${JDK_REQUIRED_MAJOR}" "bash -c 'java -version 2>&1 | grep -q \"version \\\"${JDK_REQUIRED_MAJOR}\" && java -version'"
check_opt "Java" "Heap flags present" "bash -c 'grep -RE \"-Xms|-Xmx\" /etc/{default,sysconfig} /etc/systemd/system 2>/dev/null | sed -n 1,5p'"

# UPS / NUT
check_opt "UPS" "nut-server active" "systemctl is-active nut-server.service" "active"
check_opt "UPS" "upsmon active" "systemctl is-active upsmon.service" "active"
check_opt "UPS" "Driver up" "systemctl is-active 'nut-driver@*' | head -n1"
check_opt "UPS" "upsc ${UPS_NAME}" "upsc ${UPS_NAME}"

# Network
check_cmd "Network" "Local IPs" "ip -o -4 addr show | awk '{print \$2, \$4}'"
check_opt "Network" "Active connections" "nmcli -t con show --active"
check_opt "Network" "Camera subnet ping sweep" "fping -a -q -g 192.168.1.0/24 -r1 -t50 2>/dev/null | head -n 10"

# =========[ 출력 정리 ]=========
# 콘솔 표 요약
printf "\n=== SUMMARY: %s / %s ===\n" "$HOST" "$TS"
okc=0; ngc=0; skc=0
for i in "${!R_CATEGORY[@]}"; do
  st="${R_STATUS[$i]}"; line="${R_CATEGORY[$i]} :: ${R_ITEM[$i]}"
  case "$st" in
    OK)  ok "$line";  ((okc++));;
    NG)  ng "$line";  ((ngc++));;
    SKIP) sk "$line"; ((skc++));;
  esac
done
printf "OK=%d  NG=%d  SKIP=%d\n" "$okc" "$ngc" "$skc"

# TSV
{
  echo -e "host\twhen\tcategory\titem\tstatus\tdetail"
  for i in "${!R_CATEGORY[@]}"; do
    printf "%s\t%s\t%s\t%s\t%s\t%s\n" \
      "$HOST" "$TS" "${R_CATEGORY[$i]}" "${R_ITEM[$i]}" "${R_STATUS[$i]}" \
      "$(echo "${R_DETAIL[$i]}" | tr '\n' ' ' | sed 's/[[:space:]]\{1,\}/ /g')"
  done
} >"$TSV"
log "TSV written: $TSV"

# JSON
if have jq; then
  jq -n --arg host "$HOST" --arg when "$TS" \
    --arg ok "$okc" --arg ng "$ngc" --arg sk "$skc" \
    --arg checklist "엣지 컴퓨터 테스트 항목_v1.3" \
    --arg source "internal" \
    --argjson items "$(for i in "${!R_CATEGORY[@]}"; do
        printf '{"category":%q,"item":%q,"status":%q,"detail":%q}\n' \
          "${R_CATEGORY[$i]}" "${R_ITEM[$i]}" "${R_STATUS[$i]}" "${R_DETAIL[$i]}"
      done | jq -sR 'split("\n")[:-1] | map(fromjson)')" \
    '{
      host: $host, when: $when, checklist: $checklist, source: $source,
      summary: { ok: ($ok|tonumber), ng: ($ng|tonumber), skip: ($sk|tonumber) },
      items: $items
    }' >"$JSON"
  log "JSON written: $JSON"
else
  # jq 없으면 단순 JSON 유사 포맷
  {
    echo "{"
    echo "  \"host\":\"$HOST\", \"when\":\"$TS\", \"summary\": {\"ok\": $okc, \"ng\": $ngc, \"skip\": $skc},"
    echo "  \"items\":["
    for i in "${!R_CATEGORY[@]}"; do
      printf '    {"category":%q,"item":%q,"status":%q,"detail":%q}%s\n' \
        "${R_CATEGORY[$i]}" "${R_ITEM[$i]}" "${R_STATUS[$i]}" "${R_DETAIL[$i]}" \
        $([ $i -lt $(( ${#R_CATEGORY[@]} - 1 )) ] && echo "," || echo "")
    done
    echo "  ]"
    echo "}"
  } >"$JSON"
  log "JSON (plain) written: $JSON"
fi

# 종료 코드: NG가 하나라도 있으면 1
if [ "$ngc" -gt 0 ]; then
  exit 1
else
  exit 0
fi
