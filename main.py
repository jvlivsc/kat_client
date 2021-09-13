#! /usr/bin/python3

import logging
import json
import requests
import config as cfg
import netifaces
import os
import time
import threading
import sys

from pathlib import Path
from configparser import ConfigParser
from tools import update, client_init, checks, register, system_info, announcement
from logging.handlers import RotatingFileHandler
from requests import ConnectionError
from json.decoder import JSONDecodeError


def check_param(host_data, param):
    try:
        mp_check_list = list(map(
            lambda v: (v[param]),
            host_data['roles']
        ))
    except KeyError:
        mp_check_list = []

    is_mp_checks = any(mp_check_list)

    return is_mp_checks


def threaded_update(interval=cfg.UPDATE_INTERVAL):
    logger = logging.getLogger('main.update')

    while True:
        result = update.update()
        logger.debug(f'Check updates result: {result}')
        time.sleep(interval)


def loop():
    logger = logging.getLogger('main.loop')
    host_data = {}
    host_rq = ""

    if checks.check_alive():
        rq_data = system_info.sys_info()
        is_diffs = False
        try:
            host_rq = requests.get('http://' + cfg.SERVER + '/api/host/', data=rq_data)
        except ConnectionError as connection_error:
            logger.error(f'{connection_error}')

        try:
            from_server = json.loads(host_rq.text)
            is_diffs = checks.has_differencess(rq_data, from_server)
        except JSONDecodeError as json_error:
            logger.error(f'{json_error}')

        try:
            host_data = json.loads(host_rq.text)
        except JSONDecodeError:
            host_data = {}

        if host_rq.status_code == 400 or is_diffs:
            logger.warning('Host not registered, try to register')

            info = system_info.sys_info()
            ip = info['ip']
            subnet = ip.replace(ip[ip.rfind('.') + 1:len(ip)], '0/24')
            try:
                rq_subnet = requests.get(
                    'http://' + cfg.SERVER + '/api/station/subnet/',
                    data={'name': f'{subnet}'}
                )
            except ConnectionError as request_error:
                logger.error(f'Can not get subnets with error: {request_error}')

            try:
                subnet_json = json.loads(rq_subnet.text)
                info['station'] = subnet_json['results']['station']
            except JSONDecodeError:
                subnet_json = {}

            logger.debug(f'Registration data: {info}')

            if register.register(info):
                logger.debug('Registration successfull!')
            else:
                logger.error('Registration error!')

        if host_rq.status_code == 200:
            logger.info('Host alredy registered, checking ssh tunnel')
            tunnel_up = checks.check_tunnel(host_data['ssh'], host_data['vnc'])

            if tunnel_up:
                logger.info('SSH tunnel is up.')
            else:
                logger.warning('SSH tunnel have problem!')

            send_json = {'id': host_data['pk']}
            logger.info('Try to touch server...')
            rq_touch = requests.post('http://' + cfg.SERVER + '/api/touch/', data=send_json)

            if rq_touch.status_code == 200:
                logger.info('Server touched.')
            else:
                logger.warning('Can\'t touch server!')

            if check_param(host_data, 'load_announcements'):
                station_id = host_data['station']['pk']
                announcement.sync_announcements(
                    announcement.get_announcements(station_id),
                    cfg.AUDIO_PATH
                )

    data_file = Path(cfg.DATAFILE)
    checks_data = ConfigParser()

    if data_file.is_file():
        checks_data.read(data_file)
    else:
        checks_data['DATA'] = {
            'mp': True,
            'fp': True,
            'asu': True
        }

    data = checks_data['DATA']

    mp_state = checks.check_mp()
    if check_param(host_data, 'check_mp'):
        data['mp'] = str(mp_state)

    fp_state = checks.check_fp()
    if check_param(host_data, 'check_fp'):
        data['fp'] = str(fp_state)

    asu_state = checks.check_asu()
    if check_param(host_data, 'check_asu'):
        data['asu'] = str(asu_state)

    checks_data['DATA'] = data
    with open(data_file, 'w') as conf:
        checks_data.write(conf)


def main():
    logger = logging.getLogger('main')
    logger.setLevel(cfg.LOG_LEVEL)

    file_handler = RotatingFileHandler(
        '/var/log/kat_client.log',
        maxBytes=10485760,
        backupCount=3
    )

    formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s')
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.info('---------- Run ----------')

    logger.info('> Init')

    if client_init.init():
        logger.info('Success setup initial parameters.')
    else:
        logger.warning('Trouble with setup initial parameters.')

    logger.info('> Check updates')

    update_thread = threading.Thread(target=threaded_update, daemon=True)
    update_thread.start()

    while True:
        start_time = time.time()

        loop()

        time.sleep(cfg.SLEEP)
        total_execution_time = time.time() - start_time

        if cfg.ADAPTIVE_DELAY:
            logger.info('Adaptive mode ON')

            if total_execution_time > cfg.ADAPTIVE_DELAY_VALUE:
                delta = total_execution_time - cfg.ADAPTIVE_DELAY_VALUE
                cfg.SLEEP = cfg.SLEEP - delta if (cfg.SLEEP - delta) > 0 else 1
            else:
                delta = cfg.ADAPTIVE_DELAY_VALUE - total_execution_time
                cfg.SLEEP = cfg.SLEEP + delta

            logger.debug(f'Adaptive delay: {cfg.ADAPTIVE_DELAY_VALUE}')
        else:
            logger.info('Adaptive mode OFF')

        logger.debug(f'Current delay: {total_execution_time:.1f}')


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('\nExit program')
        os._exit(0)
