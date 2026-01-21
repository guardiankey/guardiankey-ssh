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
    fail "run this uninstaller as root"
fi

SERVICE_PATHS="
/etc/systemd/system/guardiankey-ssh.service
/usr/lib/systemd/system/guardiankey-ssh.service
/lib/systemd/system/guardiankey-ssh.service
"

if need_cmd systemctl; then
    systemctl stop guardiankey-ssh.service >/dev/null 2>&1 || true
    systemctl disable guardiankey-ssh.service >/dev/null 2>&1 || true
fi

for svc in $SERVICE_PATHS; do
    if [ -f "$svc" ]; then
        rm -f "$svc"
    fi
done

if need_cmd systemctl; then
    systemctl daemon-reload >/dev/null 2>&1 || true
fi

rm -f /usr/lib/guardiankey/*.py
rmdir /usr/lib/guardiankey 2>/dev/null || true

rm -f /etc/guardiankey/gk.conf
rmdir /etc/guardiankey 2>/dev/null || true

rm -f /var/log/guardiankey.log

rm -f /etc/guardiankey/ssh.deny

echo "Uninstall complete."
