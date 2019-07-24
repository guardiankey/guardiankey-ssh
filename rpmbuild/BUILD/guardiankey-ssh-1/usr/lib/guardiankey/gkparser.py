import time
import datetime
import subprocess
import json
import re

def ParseDate(line):
        date = re.search(r'^[A-Za-z]{3}\s*[0-9]{1,2}\s[0-9]{1,2}:[0-9]{2}:[0-9]{2}', line)
        if date is not None:
            return date.group(0)

def parselog(line):
    if ("Failed" in line) or ("Accepted" in line):
        year = datetime.datetime.now().year 
        date_stamp_found = ParseDate(line)
        date_time_obj = datetime.datetime.strptime(str(year)+" "+date_stamp_found, '%Y %b %d %H:%M:%S')
        unix_time = int(time.mktime(date_time_obj.timetuple()))
        if "Failed password for" or "Failed none for" in line:
            if "nvalid user" in line:
                line_list = line.split()
                user = line_list[10]
                ip = line_list[12]
            else:
                line_list = line.split()
                user = line_list[8]
                ip = line_list[10]
        elif "Accepted password for" in line:
            line_list = line.split()
            user = line_list[8]
            ip = line_list[10]
        elif "Accepted publickey for" in line:
            line_list = line.split()
            user = line_list[8]
            ip = line_list[10]

        if "Failed" in line:
                event="M"
                event_print="Failed"
        elif "Accepted" in line:
                event="A"
                event_print="Accepted"
        else:
                event="M"
                event_print="Unknown"
        dictr={}
        dictr['time'] = unix_time
        dictr['event'] = event_print
        dictr['user'] = user
        dictr['ip'] = ip
        return json.dumps(dictr)
    else:
        nulls = {}
        nulls['user'] = 'xNull'
        return json.dumps(nulls)

