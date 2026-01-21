import time
import os

cutoff = int(time.time()) - (10 * 60)


def _parse_ts(line):
    parts = line.rsplit("#", 1)
    if len(parts) != 2:
        return None
    tail = parts[1].strip()
    if tail.startswith("gk:"):
        tail = tail[3:]
    try:
        return int(tail)
    except ValueError:
        return None


def _clean_file(path):
    if not os.path.exists(path):
        return
    with open(path, "r") as f:
        lines = f.readlines()
    with open(path, "w") as f:
        for line in lines:
            line = line.rstrip("\n")
            if not line.strip():
                continue
            ts = _parse_ts(line)
            if ts is None:
                f.write(line + "\n")
                continue
            if ts >= cutoff:
                f.write(line + "\n")


_clean_file("/etc/guardiankey/ssh.deny")
_clean_file("/etc/hosts.deny")
