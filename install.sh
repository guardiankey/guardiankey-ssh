#!/bin/sh
set -e

fail() {
    echo "ERROR: $1" >&2
    exit 1
}

need_cmd() {
    command -v "$1" >/dev/null 2>&1
}

if [ "$(id -u)" -ne 0 ]; then
    fail "run this installer as root"
fi

if ! need_cmd python3; then
    fail "python3 is not installed"
fi

if ! python3 - <<'PY'
import sys
sys.exit(0 if sys.version_info >= (3, 7) else 1)
PY
then
    fail "python3 >= 3.7 is required"
fi

if ! MISSING="$(python3 - <<'PY'
import sys
missing = []
for mod in ("requests", "configparser"):
    try:
        __import__(mod)
    except Exception:
        missing.append(mod)
if missing:
    print(" ".join(missing))
    sys.exit(1)
sys.exit(0)
PY
)"; then
    echo "Missing Python dependency: $MISSING"
    echo "Install suggestions:"
    echo "  Debian/Ubuntu: apt-get install -y python3-requests python3-configparser"
    echo "  Alma/RHEL: dnf install -y python3-requests python3-configparser"
    echo "  Fallback: pip3 install $MISSING"
    exit 1
fi

HOSTNAME="$(hostname -s 2>/dev/null || hostname || echo unknown-host)"

printf "OrgID: "
read -r ORGID
printf "authgroupID: "
read -r AUTHGROUPID
printf "key: "
read -r KEY
printf "iv: "
read -r IV

INSTALL_LIB="/usr/lib/guardiankey"
INSTALL_ETC="/etc/guardiankey"

mkdir -p "$INSTALL_LIB" "$INSTALL_ETC"

cp -a usr/lib/guardiankey/*.py "$INSTALL_LIB/"
chmod 755 "$INSTALL_LIB"
chmod 644 "$INSTALL_LIB"/*.py

if [ -f etc/cron.d/guardiankey ]; then
    cp -a etc/cron.d/guardiankey /etc/cron.d/guardiankey
    chmod 644 /etc/cron.d/guardiankey
fi

if [ -f "$INSTALL_ETC/gk.conf" ]; then
    cp -a "$INSTALL_ETC/gk.conf" "$INSTALL_ETC/gk.conf.bak.$(date +%Y%m%d%H%M%S)"
fi

SSH_LOG="/var/log/auth.log"
if [ -f /var/log/secure ]; then
    SSH_LOG="/var/log/secure"
fi

SSH_UNIT=""
if need_cmd journalctl && need_cmd systemctl; then
    UNITS="ssh.service sshd.service"
    DISCOVERED="$(systemctl list-units --type=service --all --no-legend 2>/dev/null | awk '{print $1}' | grep ssh || true)"
    for unit in $UNITS $DISCOVERED; do
        [ -n "$unit" ] || continue
        if journalctl -n 1 -u "$unit" >/dev/null 2>&1; then
            SSH_UNIT="$unit"
            break
        fi
    done
fi

cat > "$INSTALL_ETC/gk.conf" <<EOF
## GuardianKey SSH configuration
[REGISTER]
key = $KEY
iv = $IV
service = SSH
orgid = $ORGID
authgroupid = $AUTHGROUPID
agentid = $HOSTNAME
reverse = 0
block = 0
api_url = https://api.guardiankey.io
ssh_log = $SSH_LOG
ssh_unit = $SSH_UNIT
EOF

chmod 600 "$INSTALL_ETC/gk.conf"

touch /etc/guardiankey/ssh.deny
chmod 600 /etc/guardiankey/ssh.deny

HOSTS_DENY="/etc/hosts.deny"
INCLUDE_LINE="include /etc/guardiankey/ssh.deny"
if [ -f "$HOSTS_DENY" ]; then
    if grep -qF "$INCLUDE_LINE" "$HOSTS_DENY"; then
        grep -vF "$INCLUDE_LINE" "$HOSTS_DENY" > "$HOSTS_DENY.gk.tmp"
        mv "$HOSTS_DENY.gk.tmp" "$HOSTS_DENY"
    fi
fi

touch /var/log/guardiankey.log
chmod 644 /var/log/guardiankey.log

SERVICE_DIR="/etc/systemd/system"
if [ -d /usr/lib/systemd/system ]; then
    SERVICE_DIR="/usr/lib/systemd/system"
elif [ -d /lib/systemd/system ]; then
    SERVICE_DIR="/lib/systemd/system"
fi

cat > "$SERVICE_DIR/guardiankey-ssh.service" <<EOF
[Unit]
Description=GuardianKey for SSH service

[Service]
Type=simple
ExecStart=/usr/bin/python3 /usr/lib/guardiankey/gkssh.py

[Install]
WantedBy=multi-user.target
EOF

if need_cmd systemctl; then
    systemctl daemon-reload
    systemctl enable guardiankey-ssh.service
    systemctl restart guardiankey-ssh.service
fi

echo "Install complete."
