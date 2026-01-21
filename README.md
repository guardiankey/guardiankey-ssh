# GuardianKey SSH plugin

GuardianKey is a service that uses AI to increase login security. Learn more at https://guardiankey.io and https://guardiankey.io/docs.

This plugin integrates SSH authentication events with GuardianKey (GKAS). A GuardianKey account is required.

# Requirements

- Linux with systemd and journalctl
- Python 3.7+
- Python package: requests
- Root access for installation

# Install

Clone the repository and run the installer:

```sh
git clone https://github.com/guardiankey/guardiankey-ssh
cd guardiankey-ssh
sh install.sh
```

The installer will prompt for your GuardianKey configuration values and write them to `/etc/guardiankey/gk.conf`. It also installs the systemd service.

If the `requests` dependency is missing, install it with one of the following:

```sh
apt-get install -y python3-requests
```

```sh
dnf install -y python3-requests
```

```sh
pip3 install requests
```

# Configure

The configuration file is `/etc/guardiankey/gk.conf`. The installer sets:

- `orgid`
- `authgroupid`
- `key`
- `iv`
- `agentid` (hostname)

You can also set `ssh_unit` to point to a custom SSH systemd unit name. If not set, the service tries to auto-detect common units (`ssh.service`, `sshd.service`).

Additional configuration options can be set in /etc/guardiankey/gk.conf:

- `api_url` — Override the GuardianKey API endpoint (useful for on‑premise / self‑hosted GKAS). Example: `https://gkas.example.local/api/v1`
- `auto_response` — Enable automatic response/blocking of SSH attempts. Default: `0` (disabled). Set to `1` to enable automatic blocking.


# Service

Manage the service with systemd:

```sh
systemctl enable --now guardiankey-ssh
```

To restart:

```sh
systemctl restart guardiankey-ssh
```

# Uninstall

```sh
sh uninstall.sh
```

# License

This plugin is licensed under GNU/GPLv3.
