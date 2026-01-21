import time

cutoff = int(time.time()) - (10 * 60)

with open("/etc/guardiankey/ssh.deny", "r") as f:
    lines = f.readlines()

with open("/etc/guardiankey/ssh.deny", "w") as f:
    for line in lines:
        line = line.strip("\n")
        if not line:
            continue
        parts = line.split("#", 1)
        if len(parts) != 2:
            continue
        try:
            ts = int(parts[1])
        except ValueError:
            continue
        if ts >= cutoff:
            f.write(line + "\n")
