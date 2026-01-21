import time

cutoff = int(time.time()) - (10 * 60)

with open("/etc/guardiankey/ssh.deny", "r") as f:
    lines = f.readlines()

with open("/etc/guardiankey/ssh.deny", "w") as f:
    for line in lines:
        line = line.rstrip("\n")
        if not line.strip():
            continue
        parts = line.rsplit("#", 1)
        if len(parts) != 2:
            f.write(line + "\n")
            continue
        try:
            ts = int(parts[1].strip())
        except ValueError:
            f.write(line + "\n")
            continue
        if ts >= cutoff:
            f.write(line + "\n")
