import requests
import logging
import config as cfg


# register client on server
def register(data):
    try:
        rq = requests.post('http://' + cfg.SERVER + '/api/host/', data=data)
        if rq.status_code == 400:
            return False
    except ConnectionError:
        print('Connection error')
        logging.error(f'Error {ConnectionError.strerror}')
        return False

    return True
