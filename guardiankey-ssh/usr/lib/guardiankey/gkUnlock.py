import datetime

now = datetime.datetime.now() - datetime.timedelta(minutes=10)
blockdate = f"{now.hour}_{now.minute}"

with open("/etc/guardiankey/ssh.deny", "r") as f:
    lines = f.readlines()

with open("/etc/guardiankey/ssh.deny", "w") as f:
    for line in lines:
        if blockdate not in line.strip("\n"):
            f.write(line)
