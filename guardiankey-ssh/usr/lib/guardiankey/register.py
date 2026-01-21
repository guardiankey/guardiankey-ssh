import base64
import os
import requests
import md5
import json

def register(email):
	url = 'https://api.guardiankey.io/register'
	data = {}
	data['keyb64'] = base64.b64encode(os.urandom(32))
	data['ivb64']  = base64.b64encode(os.urandom(16))
	data['email'] = email
#Optionally, you can set the notification parameters, such as:
#notify_method: email or webhook
#notify_data: A base64-encoded json containing URL (if method is webhook), server and SMTP port, user, and email password.
#Example for e-mail:
# 	data['notify_method'] = 'email'
# 	data['notify_data'] = base64.b64encode('{"smtp_method":"TLS","smtp_host":"smtp.example.foo","smtp_port":"587","smtp_user":"myuser","smtp_pass":"mypass"}')
#Example for webhook:
#   data['notify_method'] = 'webhook';
# 	data['notify_data'] = base64.b64encode('{"webhook_url":"https://myorganization.com/guardiankey.php"}')
	headers = {'Content-type': 'application/x-www-form-urlencoded', 'Accept': 'text/plain'}
	query = requests.post(url, data=data, headers=headers)
	return query.text,data['keyb64'],data['ivb64']


email = raw_input( "Enter the administrator e-mail: ")
hashid,key,iv = register(email)

message = 'Put in your configuration this values:\n\
		   email: {}\n\
		   key: {}\n\
		   iv: {}\n\
		   agentid: {}\n\
                   authgrupid: {}\n\
                   organizationid: {}\n'
                   

try:
    GKIDs = json.loads(hashid)
    sucess=1
except ValueError:
    print hashid
    sucess=0

if sucess is 1:
    agentid = md5.new(os.urandom(20)).hexdigest()
    print message.format(email,key,iv,agentid,GKIDs.get("authGroupId"),GKIDs.get("organizationId"))
