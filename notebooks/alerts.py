import platform
import chime
import datetime
import os

import urllib

def chime_success():
    if platform.system() == "Linux":
        chime.success()
    elif platform.system() == "Darwin":
        os.system("say beep")
    elif platform.system() == "Windows":
        raise Exception("not handled yet")
    
    return True



def alert(success=True):
    if platform.system() == "Linux":
        if success:
            chime.success()
        else:
            chime.warning()
    elif platform.system() == "Darwin":
        os.system("say beep")
    elif platform.system() == "Windows":
        raise Exception("not handled yet")
    
    return True


def push_notifications(msg="Hello world!", push = True):
    body = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(body)

    if push:
        try:
            data = urllib.parse.urlencode({"text": body}).encode()
            req = urllib.request.Request(
                "https://api.chanify.net/v1/sender/CICswLUGEiJBQUZIR0pJQ0VVNkxUTlZCMk1DRElCWU1RSlNWMktCS0NFIgIIAQ.vj8gcfxM4jD9Zv0mBMSlFlY51EL_jC5dB8LWdWX1tAs",
                data=data,
            )
            response = urllib.request.urlopen(req)
            response.read()  # Read the response to ensure the request is complete
        except urllib.error.URLError as e:
            print(f"Error sending request: {e.reason}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        
    return True

