import subprocess
import logging

module_logger = logging.getLogger('main.update')


def update():
    update_status = subprocess.run(['bash', '../sh/update.sh'], capture_output=True)
    if update_status.returncode == 0:
        return True
    return False
