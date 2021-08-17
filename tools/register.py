import requests
import logging
import config as cfg

from requests import ConnectionError

module_logger = logging.getLogger('main.register')


# register client on server
def register(data):
    logger = logging.getLogger('main.register.register')
    try:
        rq = requests.post('http://' + cfg.SERVER + '/api/host/', data=data)
        if rq.status_code == 400:
            return False
    except ConnectionError as connection_error:
        logger.error(f'Error {connection_error}')
        return False

    return True
