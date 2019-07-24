import guardiankey
import gkparser
import sys
import json
import configparser
import datetime
import tail


configp = configparser.ConfigParser()
configp.read('/etc/guardiankey/gk.conf')
GKconfig = configp['REGISTER']

def callback_f(line):
    send(line)

def doAction(ip):
    now = datetime.datetime.now()
    blockdate = str(now.hour)+"_"+str(now.minute)
    ipline = str(ip)+'#'+blockdate+'\n'
    f = open('/etc/guardiankey/ssh.deny','a')
    f.write(ipline)
    f.close()

def send(line):
    global GKconfig
    jlog = json.loads(gkparser.parselog(line))
    if jlog['user'] <> 'xNull':
        if jlog['event'] == "Accepted":
            loginfailed = 0
        else:
            loginfailed = 1
        result = guardiankey.checkaccess(jlog['user'],jlog['ip'],jlog['time'],loginfailed,'Authentication')
        if result['response'] == 'BLOCK' and GKconfig['block'] == '1':
            f = open('/var/log/guardiankey.log','a')
            f.write(json.dumps(result))
            f.close()
            doAction(jlog['ip'])

        return result
    
while True:
    if GKconfig['key'] is None:
        print "You need configure /etc/guardiankey/gk.conf!"
        quit()
    t = tail.Tail(GKconfig['ssh_log'])
    t.register_callback(callback_f)
    t.follow(s=1)
