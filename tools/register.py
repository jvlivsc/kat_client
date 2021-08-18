import requests
import logging
import config as cfg

from requests import ConnectionError

module_logger = logging.getLogger('main.register')


# register client on server
def register(data):
    logger = logging.getLogger('main.register.register')
    logger.info('> Register HOST information')

    try:
        rq = requests.post('http://' + cfg.SERVER + '/api/host/', data=data)
        if rq.status_code == 400:
            logger.error('Registration error with code 400')
            return False
    except ConnectionError as connection_error:
        logger.error(f'Registration error with error message: {connection_error}')
        return False

    logger.info('Registration successful')
    return True
