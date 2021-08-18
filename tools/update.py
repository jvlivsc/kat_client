import subprocess
import logging

module_logger = logging.getLogger('main.update')


def update():
    logger = logging.getLogger('main.update.update')
    logger.info('> Update scripts')

    update_status = subprocess.run(['bash', '../sh/update.sh'], capture_output=True)

    logger.debug(f'Update status code: {update_status.returncode}')

    if update_status.returncode == 0:
        logger.info('Update successful')
        return True

    logger.error('Update error')
    return False
