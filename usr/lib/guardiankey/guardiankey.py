import json
import base64
import time
import socket
import requests
from Crypto.Cipher import AES
from _socket import timeout
import configparser

configp = configparser.ConfigParser()
configp.read('/etc/guardiankey/gk.conf')
GKconfig = configp['REGISTER']



def getUserAgent():
    #...
    UA=""
    return UA

def create_message(username,ip,eventtime,loginfailed=0,eventType='Authentication'):
    global GKconfig
    keyb64      = GKconfig['key']
    ivb64       = GKconfig['iv']
    agentid     = GKconfig['agentid']
    orgid       = GKconfig['orgid']
    authgroupid = GKconfig['authgroupid']
    reverse     = GKconfig['reverse']
    timestamp   = eventtime
    
    if agentid is not None:
        key = base64.b64decode(keyb64)
        iv  = base64.b64decode(ivb64)
        clientIP = ip
        UA = getUserAgent()
        sjson = {}
        sjson['generatedTime'] = timestamp
        sjson['agentId'] = agentid
        sjson['organizationId'] = orgid
        sjson['authGroupId'] = authgroupid
        sjson['service'] = GKconfig['service']
        sjson['clientIP'] = clientIP
        try:
            sjson['clientReverse'] = socket.gethostbyaddr(clientIP)[0] if reverse else ""
        except:
            sjson['clientReverse'] = ""
        sjson['userName'] = username
        sjson['authMethod'] = ''
        sjson['loginFailed'] = str(loginfailed)
        sjson['userAgent'] = UA
        sjson['psychometricTyped'] = ''
        sjson['psychometricImage'] = ''
        sjson['event_type'] = eventType
        message = json.dumps(sjson)
        obj = AES.new(key,AES.MODE_CFB, iv, segment_size=8)
        cryptmessage = base64.b64encode(obj.encrypt(message))
        return cryptmessage
        
def sendevent(username,loginfailed=0,eventType='Authentication'):
    global GKconfig
    message = create_message(username,userEmail,loginfailed,eventType)
    tmpdata = {}
    tmpdata['id'] = GKconfig['authgroupid']
    tmpdata['message'] = message
    data = json.dumps(tmpdata)
    url = GKconfig['api_url']+'/sendevent'
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    try:
        requests.post(url, data=data, headers=headers, timeout=4)
        return ""
    except:
        return ""

def checkaccess(username,ip,eventtime,loginfailed=0,eventType='Authentication'):
    global GKconfig
    message = create_message(username,ip,eventtime,loginfailed,eventType)
    tmpdata = {}
    tmpdata['id'] = GKconfig['authgroupid']
    tmpdata['message'] = message
    data = json.dumps(tmpdata)
    url = GKconfig['api_url']+'/checkaccess'
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    try:
        query = requests.post(url, data=data, headers=headers, timeout=4)
        gkreturn = json.loads(query.text)
        return gkreturn
        
    except:
        return {"response":"ERROR"}

