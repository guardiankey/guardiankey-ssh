import guardiankey
import gkparser
import sys
import json
import configparser
import datetime
import tail
import subprocess
import os
import signal

configp = configparser.ConfigParser()
configp.read('/etc/guardiankey/gk.conf')
GKconfig = configp['REGISTER']
def doAction(ip):
    now = datetime.datetime.now()
    blockdate = int(now.timestamp())
    ipline = f"sshd,ssh: {ip} #{blockdate}\n"
    with open('/etc/guardiankey/ssh.deny', 'a') as f:
        f.write(ipline)


def _kill_ssh_sessions(username, ip):
    try:
        res = subprocess.run(
            ['ps', '-eo', 'pid,user,args'],
            capture_output=True, text=True, timeout=2
        )
        if res.returncode != 0:
            return
        lines = res.stdout.splitlines()
        candidates = []
        for line in lines[1:]:
            parts = line.split(None, 2)
            if len(parts) < 3:
                continue
            pid, user, args = parts
            if user != username:
                continue
            if 'sshd:' not in args:
                continue
            candidates.append((pid, args))

        if not candidates:
            return

        matched = []
        for pid, args in candidates:
            if f"rhost={ip}" in args or f"@{ip}" in args:
                matched.append(pid)

        target_pids = matched if matched else [pid for pid, _ in candidates]
        for pid in target_pids:
            try:
                os.kill(int(pid), signal.SIGKILL)
            except Exception:
                continue
    except Exception:
        return


def send(line):
    global GKconfig
    jlog = json.loads(gkparser.parselog(line))
    if jlog.get('user') != 'xNull':
        if jlog.get('event') == "Accepted":
            loginfailed = 0
        else:
            loginfailed = 1
        result = guardiankey.checkaccess(jlog.get('user'), jlog.get('ip'), jlog.get('time'), loginfailed, 'Authentication')
        if result.get('response') == 'BLOCK' and GKconfig.get('block') == '1':
            with open('/var/log/guardiankey.log', 'a') as f:
                f.write(json.dumps(result) + '\n')
            doAction(jlog.get('ip'))
            _kill_ssh_sessions(jlog.get('user'), jlog.get('ip'))

        return result


def _candidate_units():
    units = []
    conf_unit = GKconfig.get('ssh_unit', '').strip()
    if conf_unit:
        units.append(conf_unit)
    units.extend(['ssh.service', 'sshd.service'])
    return units


def _discover_units():
    try:
        res = subprocess.run(
            ['systemctl', 'list-units', '--type=service', '--all', '--no-legend'],
            capture_output=True, text=True, timeout=3
        )
        if res.returncode != 0:
            return []
        found = []
        for line in res.stdout.splitlines():
            parts = line.split()
            if not parts:
                continue
            unit = parts[0]
            if 'ssh' in unit:
                found.append(unit)
        return found
    except FileNotFoundError:
        return []
    except Exception:
        return []


def use_journalctl():
    """Check if journalctl is available and has ssh logs"""
    global JOURNAL_UNIT
    JOURNAL_UNIT = None
    units = _candidate_units()
    units.extend(_discover_units())
    seen = set()
    try:
        for unit in units:
            if not unit or unit in seen:
                continue
            seen.add(unit)
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
