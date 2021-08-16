import os
import netifaces
import logging
import subprocess

module_logger = logging.getLogger('main.client_init')


def init():
    logger = logging.getLogger('main.client_init.init')
    dir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir)
    iface = filter(lambda str: 'en' in str, netifaces.interfaces())
    iface = list(iface)
    if len(iface) > 1:
        init_status = subprocess.run(
            ['bash', '../sh/init.sh', iface[0], iface[1]],
            capture_output=True
        )
        logger.debug(f'Return code for init.sh: {init_status.returncode}')
        if init_status.returncode == 0:
            return True
    return False
