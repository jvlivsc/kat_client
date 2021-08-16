import logging
import config as cfg
import subprocess
import netifaces
import requests

module_logger = logging.getLogger('main.checks')


# checks is server alive
def check_alive():
    logger = logging.getLogger('main.checks.check_alive')
    result = subprocess.run(
        ['ping', '-c', '1', cfg.SERVER],
        capture_output=True
    )
    logger.debug(f'Return code for check_alive ping: {result.returncode}')
    if result.returncode == 0:
        return True
    return False


def check_asu():
    logger = logging.getLogger('main.checks.check_asu')
    logger.info('> Server ASU')

    result = False

    server_status = subprocess.run(
        ['ping', '-c', '1', cfg.ASU_SERVER],
        capture_output=True
    )
    logger.debug(f'Return code for asu ping: {server_status.returncode}')
    if server_status.returncode == 0:
        try:
            rq = requests.get('http://' + cfg.ASU_SERVER + ':5000/bush-api/ns/trips/292/all?showAll=false')
            if rq.status_code == 200:
                result = True
        except ConnectionError:
            logger.error(f'{ConnectionError.strerror}')

    logger.info(f'Server check result: {result}')
    return result


def check_mp():
    logger = logging.getLogger('main.checks.check_mp')
    logger.info('> Matrix printer')
    mp_status = subprocess.run(['bash', '../sh/mp.sh'], capture_output=True)
    logger.debug(f'Return code for mp.sh: {mp_status.returncode}')

    result = True if mp_status.returncode == 0 else False
    logger.info(f'Matrix printer check result: {result}')
    return result


def check_fp():
    logger = logging.getLogger('main.checks.check_fp')
    logger.info('> Fiscal printer')

    iface = filter(lambda str: 'en' in str, netifaces.interfaces())
    iface = list(iface)

    result = False

    if len(iface) > 1:
        fp_status = subprocess.run(
            ['bash', '../sh/fp.sh', iface[0], iface[1]],
            capture_output=True
        )
        logger.debug(f'Return code for fp.sh: {fp_status.returncode}')
        if fp_status.returncode == 0:
            result = True

    logger.info(f'Fiscal printer check result: {result}')
    return result


def check_tunnel(ssh, vnc):
    logger = logging.getLogger('main.checks.check_tunnel')
    result = subprocess.run(
        ['bash', '../sh/tunnel.sh', cfg.SERVER, cfg.USER, str(ssh), str(vnc)],
        capture_output=False
    )
    logger.debug(f'Return code for tunnel.sh: {result.returncode}')
    if result.returncode == 0:
        return True
    return False
