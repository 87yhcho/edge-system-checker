#!/usr/bin/env bash
# NUT + upssched 자동 셋업 스크립트 (Ubuntu 24.04)
# - 정전(ONBATT) 120s 지속 시 FSD -> 안전종료
# - 상전원 복구 시 타이머 취소
# - UPS 파워차단(killpower) 준비
# 실행: sudo bash setup_nut.sh

set -euo pipefail

### 변수(필요 시 수정)
UPS_NAME="ups"
DRIVER="usbhid-ups"
PORT="auto"                # /dev/hidrawX 대신 auto 권장
VENDORID="051d"
PRODUCTID="0003"
DESC="APC SMC1500IC"

MONUSER="monuser"
MONPASS="secret"

ADMINUSER="adminuser"      # upsrw/instcmds 허용 사용자
ADMINPASS="adminpass"

UFW_NET="192.168.10.0/24"  # NUT TCP 3493 허용대역
ONBATT_DELAY=120           # 정전 지속 시 종료 타이머(초)
UPS_DELAY_SHUTDOWN=5       # UPS 자체 종료 딜레이(초)
FORCEPOW_DELAY=60          # (옵션) 강제 전원차단 보조 스크립트 지연

### 사전 확인
if [[ $EUID -ne 0 ]]; then
  echo "root 권한으로 실행하세요: sudo bash $0" >&2
  exit 1
fi

timestamp() { date +%Y%m%d-%H%M%S; }
bkp() { local f="$1"; [[ -f "$f" ]] && cp -a "$f" "${f}.bak.$(timestamp)"; }

echo "[1/8] 패키지 설치"
apt-get update -y
DEBIAN_FRONTEND=noninteractive apt-get install -y nut nut-client nut-server dos2unix ufw || true

echo "[2/8] 설정 디렉터리 및 권한"
install -d -m 755 /etc/nut
install -d -m 755 /usr/lib/systemd/system-shutdown

echo "[3/8] 설정 파일 백업"
bkp /etc/nut/ups.conf
bkp /etc/nut/nut.conf
bkp /etc/nut/upsd.users
bkp /etc/nut/upsd.conf
bkp /etc/nut/upsmon.conf
bkp /etc/nut/upssched.conf
bkp /etc/nut/upssched-cmd
bkp /usr/lib/systemd/system-shutdown/99-force-poweroff

echo "[4/8] 설정 파일 생성"

cat >/etc/nut/ups.conf <<EOF
[${UPS_NAME}]
  driver    = ${DRIVER}
  port      = ${PORT}
  vendorid  = ${VENDORID}
  productid = ${PRODUCTID}
  desc      = "${DESC}"
  override.ups.start.auto = yes
  override.ups.start.battery = yes
EOF

cat >/etc/nut/nut.conf <<'EOF'
MODE=standalone
EOF

# 모니터 사용자 + 관리자(SET/instcmds) 사용자 구성
cat >/etc/nut/upsd.users <<EOF
[${MONUSER}]
  password = ${MONPASS}
  upsmon master

[${ADMINUSER}]
  password = ${ADMINPASS}
  actions = SET
  instcmds = ALL
EOF
chmod 640 /etc/nut/upsd.users
chown root:nut /etc/nut/upsd.users || true

# 원격 접근 필요 시 LISTEN 바인딩 (내부망 한정)
cat >/etc/nut/upsd.conf <<'EOF'
LISTEN 0.0.0.0 3493
EOF

# upsmon: upssched 사용, 각종 타이밍/알림 설정
cat >/etc/nut/upsmon.conf <<EOF
MONITOR ${UPS_NAME}@localhost 1 ${MONUSER} ${MONPASS} master
MINSUPPLIES 1
SHUTDOWNCMD "/sbin/shutdown -h now"
POWERDOWNFLAG /etc/killpower
FINALDELAY 1

POLLFREQ 5
POLLFREQALERT 5
HOSTSYNC 15
DEADTIME 120

NOTIFYCMD /usr/sbin/upssched

NOTIFYFLAG ONLINE   SYSLOG+EXEC
NOTIFYFLAG ONBATT   SYSLOG+EXEC
NOTIFYFLAG LOWBATT  SYSLOG+EXEC
NOTIFYFLAG FSD      SYSLOG+EXEC
NOTIFYFLAG COMMOK   SYSLOG
NOTIFYFLAG COMMBAD  SYSLOG

RBWARNTIME 43200
NOCOMMWARNTIME 300
EOF

# upssched: ONBATT 시 타이머 시작, ONLINE 시 취소, 타이머 만료 시 FSD
cat >/etc/nut/upssched.conf <<EOF
CMDSCRIPT /etc/nut/upssched-cmd
PIPEFN /var/run/nut/upssched.pipe
LOCKFN /var/run/nut/upssched.lock

AT ONBATT * EXECUTE log-onbatt
AT ONBATT * START-TIMER ob${ONBATT_DELAY} ${ONBATT_DELAY}
AT TIMER  ob${ONBATT_DELAY} EXECUTE trigger-fsd
AT FSD * EXECUTE force-poweroff
AT ONLINE * CANCEL-TIMER ob${ONBATT_DELAY}
AT ONLINE * EXECUTE log-online
EOF

# sudo 사용 금지(중요). upsmon -c fsd 직접 호출.
cat >/etc/nut/upssched-cmd <<'EOF'
#!/bin/sh
logger -t upssched-cmd "EXECUTE: $1 (user: $(whoami))"

case "$1" in
  trigger-fsd|ob*)
    logger -t upssched-cmd "Timer expired -> upsmon -c fsd"
    /usr/sbin/upsmon -c fsd
    ;;
  force-poweroff)
    # (옵션) 보조 강제전원차단 스크립트 호출
    /usr/bin/env DELAY="${DELAY:-60}" /usr/lib/systemd/system-shutdown/99-force-poweroff &
    ;;
  log-onbatt)
    logger -t upssched-cmd "ONBATT timer started"
    ;;
  log-online)
    logger -t upssched-cmd "ONLINE timer canceled"
    ;;
  *)
    logger -t upssched-cmd "unknown EXECUTE: $1"
    ;;
esac
EOF
chmod 0755 /etc/nut/upssched-cmd

# (옵션) 강제 전원차단 보조 스크립트
cat >/usr/lib/systemd/system-shutdown/99-force-poweroff <<'EOF'
#!/bin/sh
# 사용자 공간에서도 호출 가능하도록 작성
# 환경변수 DELAY(초) 후 강제 전원차단
D="${DELAY:-60}"
echo "99-force-poweroff: sleep ${D}s then FORCE POWEROFF" >&2
sleep "$D"
# 가능한 한 확실히 종료
/sbin/poweroff -f || /sbin/shutdown -P now || /usr/sbin/poweroff || /bin/systemctl poweroff
EOF
chmod 0755 /usr/lib/systemd/system-shutdown/99-force-poweroff

# 텍스트 형태/개행 정규화
dos2unix /etc/nut/upssched.conf /etc/nut/upssched-cmd /etc/nut/upsmon.conf >/dev/null 2>&1 || true

echo "[5/8] UFW(선택) 3493 허용"
ufw allow from "${UFW_NET}" to any port 3493 proto tcp >/dev/null 2>&1 || true

echo "[6/8] 부팅 시 UPS 파라미터 적용 서비스 생성 (ups.delay.shutdown=${UPS_DELAY_SHUTDOWN}s)"
cat >/etc/systemd/system/ups-parameters.service <<EOF
[Unit]
Description=Set custom UPS parameters at boot
After=nut-server.service
Wants=nut-server.service

[Service]
Type=oneshot
ExecStart=/usr/bin/upsrw -s ups.delay.shutdown=${UPS_DELAY_SHUTDOWN} -u ${ADMINUSER} -p ${ADMINPASS} ${UPS_NAME}@localhost

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload

echo "[7/8] NUT 서비스 활성화 및 초기화 순서 적용"
# 깨끗한 재시작(파이프/락 정리)
systemctl stop nut-monitor || true
systemctl stop nut-server || true
pkill -9 upssched 2>/dev/null || true
pkill -9 upsmon   2>/dev/null || true
rm -f /var/run/nut/upssched.pipe /var/run/nut/upssched.lock 2>/dev/null || true

# 드라이버/서버/모니터 순으로 시작
systemctl enable nut-driver@${UPS_NAME}.service nut-server.service nut-monitor.service ups-parameters.service
systemctl start  nut-driver@${UPS_NAME}.service
systemctl start  nut-server.service
systemctl start  nut-monitor.service
systemctl start  ups-parameters.service || true

echo "[8/8] 요약 확인"
echo " - 드라이버 상태:"
systemctl --no-pager --full status nut-driver@${UPS_NAME}.service | sed -n '1,20p' || true
echo " - 서버 리슨(3493) 확인:"
ss -tlnp | grep 3493 || true
echo " - UPS 질의:"
upsc ${UPS_NAME}@localhost 2>/dev/null | head -n 30 || true

echo "완료. ONBATT ${ONBATT_DELAY}s 지속 시 FSD -> 안전종료 동작."
