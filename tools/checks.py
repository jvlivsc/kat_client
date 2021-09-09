import logging
import config as cfg
import subprocess
import netifaces
import requests

from requests import ConnectionError

module_logger = logging.getLogger('main.checks')


# checks is server alive
def check_alive():
    logger = logging.getLogger('main.checks.check_alive')
    logger.info(f'Checking {cfg.SERVER} is alive')
    result = subprocess.run(
        ['ping', '-c', '3', cfg.SERVER],
        capture_output=True
    )
    logger.debug(f'Return code for check_alive ping: {result.returncode}')
    if result.returncode == 0:
        logger.info(f'{cfg.SERVER} is ONLINE')
        return True

    logger.warning(f'{cfg.SERVER} is OFFLINE')
    return False


def check_asu():
    logger = logging.getLogger('main.checks.check_asu')
    logger.info('> Server ASU')

    result = False

    logger.info(f'Checking {cfg.ASU_SERVER} is alive')

    server_status = subprocess.run(
        ['ping', '-c', '3', cfg.ASU_SERVER],
        capture_output=True
    )

    logger.debug(f'Return code for asu ping: {server_status.returncode}')

    if server_status.returncode == 0:
        logger.info(f'{cfg.ASU_SERVER} is ONLINE')
        logger.info(f'Checking {cfg.ASU_SERVER} services is accessible')

        try:
            rq = requests.get('http://' + cfg.ASU_SERVER + ':5000/bush-api/ns/trips/292/all?showAll=false')

            if rq.status_code == 200:
                logger.info(f'{cfg.ASU_SERVER} services is accessible')
                result = True
        except ConnectionError as connection_error:
            logger.error(f'{cfg.ASU_SERVER} is not accessible with error: {connection_error}')
    else:
        logger.warning(f'{cfg.ASU_SERVER} is OFFLINE')

    return result


def check_mp():
    logger = logging.getLogger('main.checks.check_mp')
    logger.info('> Matrix printer')

    mp_status = subprocess.run(['bash', '../sh/mp.sh'], capture_output=True)

    logger.debug(f'Return code for mp.sh: {mp_status.returncode}')

    result = True if mp_status.returncode == 0 else False

    if result:
        logger.info('Matrix printer connected')
    else:
        logger.warning('Matrix printer disconnected')

    return result


def check_fp():
    logger = logging.getLogger('main.checks.check_fp')
    logger.info('> Fiscal printer')

    iface = filter(lambda str: 'en' in str, netifaces.interfaces())
    iface = list(iface)

    result = False

    if len(iface) > 1:
        logger.info('Setting up fiscal printer')
        fp_status = subprocess.run(
            ['bash', '../sh/fp.sh', iface[0], iface[1]],
            capture_output=False
        )
        logger.debug(f'Return code for fp.sh: {fp_status.returncode}')
        if fp_status.returncode == 0:
            result = True

    if result:
        logger.info('Fiscal printer connected')
    else:
        logger.warning('Fiscal printer disconnected')

    return result


def check_tunnel(ssh, vnc):
    logger = logging.getLogger('main.checks.check_tunnel')
    logger.info('> SSH tunnels control')

    result = subprocess.run(
        ['bash', '../sh/tunnel.sh', cfg.SERVER, cfg.USER, str(ssh), str(vnc)],
        capture_output=False
    )
    logger.debug(f'Return code for tunnel.sh: {result.returncode}')
    if result.returncode == 0:
        logger.info('> SSH tunnels is up')
        return True
    else:
        logger.warning('> SSH tunnel is down')

    return False


def has_differencess(info, rq):
    local_ip = info['ip']
    stored_ip = rq['ip']
    local_mac = info['mac']
    stored_mac = rq['mac']
    local_hostname = info['hostname']
    stored_hostname = rq['hostname']

    if local_ip == stored_ip and local_mac == stored_mac and local_hostname == stored_hostname:
        result = False
    else:
        result = True

    return result
