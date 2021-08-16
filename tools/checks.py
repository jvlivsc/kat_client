import logging
import config as cfg
import subprocess
import netifaces
import requests


# checks is server alive
def check_alive():
    result = subprocess.run(
        ['ping', '-c', '1', cfg.SERVER],
        capture_output=True
    )
    logging.debug(f'Return code for check_alive ping: {result.returncode}')
    if result.returncode == 0:
        return True
    return False


def asu_check():
    server_status = subprocess.run(
        ['ping', '-c', '1', cfg.ASU_SERVER],
        capture_output=True
    )
    logging.debug(f'Return code for asu_check ping: {server_status.returncode}')
    if server_status.returncode == 0:
        try:
            rq = requests.get('http://' + cfg.ASU_SERVER + ':5000/bush-api/ns/trips/292/all?showAll=false')
            if rq.status_code == 200:
                return True
        except ConnectionError:
            print('Connection error')
            logging.error(f'{ConnectionError.strerror}')
    return False


def mp_check():
    mp_status = subprocess.run(['bash', '../sh/mp.sh'], capture_output=True)
    logging.debug(f'Return code for mp.sh: {mp_status.returncode}')
    if mp_status.returncode == 0:
        return True
    return False


def fp_check():
    iface = filter(lambda str: 'en' in str, netifaces.interfaces())
    iface = list(iface)

    if len(iface) > 1:
        fp_status = subprocess.run(
            ['bash', '../sh/fp.sh', iface[0], iface[1]],
            capture_output=True
        )
        logging.debug(f'Return code for fp.sh: {fp_status.returncode}')
        if fp_status.returncode == 0:
            return True
    return False


def tunnel_check(ssh, vnc):
    result = subprocess.run(
        ['bash', '../sh/tunnel.sh', cfg.SERVER, cfg.USER, str(ssh), str(vnc)],
        capture_output=False
    )
    logging.debug(f'Return code for tunnel.sh: {result.returncode}')
    if result.returncode == 0:
        return True
    return False
