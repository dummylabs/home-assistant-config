import sys
import telnetlib
import re
from secrets import get_secret

# your router creds
IP = get_secret('ndms_host')
LOGIN = get_secret('ndms_user')
PWD = get_secret('ndms_password')
# router interface (Home by default)
MAC = CMD = None
TIMEOUT = 5
STATUS_REGEXP = 'access: (.*)\r'

if len(sys.argv) != 3 or sys.argv[2] not in ['deny','permit','status']:
    print("""Usage:
           python3 access.py mydevice deny 
           python3 access.py mydevice permit
           where mydevice is the MAC address of a device in the secrets.yaml""")
    sys.exit(-1)
else:
    CMD = sys.argv[2]
    MAC = get_secret(sys.argv[1])

class Telnet(object):
    def send_command(self, cmd, prompt):
        result = self.tn.expect([prompt.encode('utf-8')],TIMEOUT)
        if result[0] == -1:
            print('Something went wrong, exited')
            print(result)
            sys.exit(-1)
        self.tn.write((cmd+'\n').encode('utf-8'))

    def read_status(self):
        self.send_command(f"show ip hotspot {MAC}", "\(config\)\> ")
        pattern = re.compile(STATUS_REGEXP)
        output = ttn.tn.expect([STATUS_REGEXP.encode('utf-8')],5)
        result = pattern.findall(output[2].decode('utf-8'))
        return result

    def __init__(self, tn_ip, user, password):
        self.tn = telnetlib.Telnet(tn_ip, 23, 15)
        #self.tn.set_debuglevel(100)
        self.send_command(user, 'Login: ')
        self.send_command(password, 'Password: ')

try:
    ttn = Telnet(IP,LOGIN,PWD)
    if CMD in ['deny','permit']:
        ttn.send_command(f"ip hotspot host {MAC} {CMD}", "\(config\)\> ")
        ttn.send_command("exit", 'applied to host')
    else:
        status = ttn.read_status()
        if len(status) > 0:
            if status[0] == 'permit':
                print('ACCESS GRANTED')
                sys.exit(0)
            elif status[0] == 'deny':
                print('ACCESS DENIED')
                sys.exit(1)
        print('UNKNOWN STATE')
        sys.exit(-1)                
        
except Exception as e:
    print("Unexpected error:", e)
