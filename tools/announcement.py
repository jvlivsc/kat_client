from json.decoder import JSONDecodeError
from posix import listdir
import requests
import json
import config as cfg
import subprocess
import os
import logging

module_logger = logging.getLogger('main.announce')


def get_announcements(id):
    logger = logging.getLogger('main.announce.get')
    logger.info(f'Get announcements list from {cfg.SERVER}')
    url = 'http://' + cfg.SERVER + '/api/storage/announcements/'
    file_list = []
    try:
        rq = requests.get(url, data={'id': id})
        logger.debug(f'Announcements request: {rq}')
    except requests.ConnectionError as e:
        print(e.strerror)
        logger.debug(f'Request error: {e.strerror}')

    logger.info('Parsing request...')

    try:
        url_json = json.loads(rq.text)

        logger.debug(f'Request json: {url_json}')

        if url_json['success']:
            for j in url_json['results']:
                file_list.append('http://' + cfg.SERVER + j['file'])
        else:
            print(url_json['results'])

        logger.debug(f'Parsed list: {file_list}')

    except json.JSONDecodeError as e:
        print(e)
        logger.error(f'Json decode error: {e}')

    return file_list


def sync_announcements(urls, folder):
    logger = logging.getLogger('main.announce.sync')
    logger.info(f'Sync files from server {cfg.SERVER} and local dir {cfg.AUDIO_PATH}')
    dir = cfg.AUDIO_PATH
    files = os.listdir(dir)
    files_to_rm = [file for file in files if not any(file in url for url in urls)]

    for file in files_to_rm:
        os.remove(os.path.join(dir, file))

    for url in urls:
        wget = subprocess.run(['wget', '-m', url, '-nd', '-P', folder], capture_output=True)

        logger.debug(f'Sync result for {url}: {wget.stdout}')

    logger.info('End sync')

    return wget.stdout
