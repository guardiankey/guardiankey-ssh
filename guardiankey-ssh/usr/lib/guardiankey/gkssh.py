import guardiankey
import gkparser
import sys
import json
import configparser
import datetime
import tail
import subprocess

configp = configparser.ConfigParser()
configp.read('/etc/guardiankey/gk.conf')
GKconfig = configp['REGISTER']
def doAction(ip):
    now = datetime.datetime.now()
    blockdate = f"{now.hour}_{now.minute}"
    ipline = f"{ip}#{blockdate}\n"
    with open('/etc/guardiankey/ssh.deny', 'a') as f:
        f.write(ipline)


def send(line):
    global GKconfig
    jlog = json.loads(gkparser.parselog(line))
    if jlog.get('user') != 'xNull':
        if jlog.get('event') == "Accepted":
            loginfailed = 0
        else:
            loginfailed = 1
        result = guardiankey.checkaccess(jlog.get('user'), jlog.get('ip'), jlog.get('time'), loginfailed, 'Authentication')
        if result.get('response') == 'ACCEPT' and GKconfig.get('block') == '1':
            with open('/var/log/guardiankey.log', 'a') as f:
                f.write(json.dumps(result) + '\n')
            doAction(jlog.get('ip'))

        return result


def use_journalctl():
    """Check if journalctl is available and has ssh logs (ssh.service or sshd.service)"""
    global JOURNAL_UNIT
    JOURNAL_UNIT = None
    units = ['ssh.service', 'sshd.service']
    try:
        for unit in units:
            res = subprocess.run(['journalctl', '-n', '1', '-u', unit],
                                 capture_output=True, text=True, timeout=2)
            if res.returncode == 0 and res.stdout.strip():
                JOURNAL_UNIT = unit
                return True
        return False
    except FileNotFoundError:
        return False
    except Exception:
        return False


while True:
    if not GKconfig.get('key'):
        print("You need to configure /etc/guardiankey/gk.conf!")
        sys.exit(1)
    
    if use_journalctl():
        cmd = ['journalctl', '-f', '-o', 'cat', '-u', JOURNAL_UNIT]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)
        for line in proc.stdout:
            send(line.strip())
    else:
        t = tail.Tail(GKconfig.get('ssh_log'))
        t.register_callback(send)
        t.follow(s=1)
