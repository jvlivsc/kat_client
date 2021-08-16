import os
import netifaces
import logging
import subprocess


def init():
    dir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir)
    iface = filter(lambda str: 'en' in str, netifaces.interfaces())
    iface = list(iface)
    if len(iface) > 1:
        init_status = subprocess.run(
            ['bash', 'init.sh', iface[0], iface[1]],
            capture_output=True
        )
        logging.debug(f'Return code for init.sh: {init_status.returncode}')
        if init_status.returncode == 0:
            return True
    return False
