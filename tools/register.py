import requests
import logging
import config as cfg

module_logger = logging.getLogger('main.register')


# register client on server
def register(data):
    logger = logging.getLogger('main.register.register')
    try:
        rq = requests.post('http://' + cfg.SERVER + '/api/host/', data=data)
        if rq.status_code == 400:
            return False
    except ConnectionError:
        print('Connection error')
        logger.error(f'Error {ConnectionError.strerror}')
        return False

    return True
