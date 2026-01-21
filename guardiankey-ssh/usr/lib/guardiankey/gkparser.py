import time
import datetime
import json
import re

def ParseDate(line):
    m = re.search(r'^[A-Za-z]{3}\s+[0-9]{1,2}\s[0-9]{1,2}:[0-9]{2}:[0-9]{2}', line)
    return m.group(0) if m else None

def parselog(line):
    if ("Failed" in line) or ("Accepted" in line):
        year = datetime.datetime.now().year
        date_stamp_found = ParseDate(line)
        if date_stamp_found:
            try:
                date_time_obj = datetime.datetime.strptime(f"{year} {date_stamp_found}", '%Y %b %d %H:%M:%S')
            except ValueError:
                date_time_obj = None
        else:
            date_time_obj = None

        unix_time = int(time.mktime(date_time_obj.timetuple())) if date_time_obj else int(time.time())

        text = line.strip()
        lower = text.lower()

        user = 'xNull'
        ip = 'xNull'

        # Try regexes for common sshd log formats (case-insensitive)
        patterns = [
            r'Invalid user\s+(\S+)\s+from\s+(\S+)',  # Invalid user <user> from <ip>
            r'Failed (?:password|none) for invalid user\s+(\S+)\s+from\s+(\S+)',  # Failed ... for invalid user <user> from <ip>
            r'Failed (?:password|none) for\s+(\S+)\s+from\s+(\S+)',  # Failed password for <user> from <ip>
            r'Accepted (?:password|publickey) for\s+(\S+)\s+from\s+(\S+)',  # Accepted ... for <user> from <ip>
        ]
        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                user = m.group(1)
                ip = m.group(2)
                break

        # Fallback: try simple splitting if regexes didn't match
        if user == 'xNull' and ip == 'xNull':
            parts = text.split()
            try:
                # best-effort: many syslog lines put user at index 8 and ip at 10
                if len(parts) > 10:
                    user = parts[8]
                    ip = parts[10]
                elif len(parts) > 6:
                    user = parts[6]
                    ip = parts[-1]
            except Exception:
                user = 'xNull'
                ip = 'xNull'

        if "Failed" in line:
            event = "M"
            event_print = "Failed"
        elif "Accepted" in line:
            event = "A"
            event_print = "Accepted"
        else:
            event = "M"
            event_print = "Unknown"

        dictr = {
            'time': unix_time,
            'event': event_print,
            'user': user,
            'ip': ip,
        }
        return json.dumps(dictr)
    else:
        return json.dumps({'user': 'xNull'})
