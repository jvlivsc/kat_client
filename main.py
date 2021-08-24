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


def check_param(host_data, param, check):
    value = False
    try:
        mp_check_list = list(map(
            lambda v: (v[param]),
            host_data['roles']
        ))
    except KeyError:
        mp_check_list = []

    is_mp_checks = any(mp_check_list)

    if is_mp_checks:
        mp_check_result = check
        if mp_check_result:
            value = True
        else:
            value = False

    return value


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
            rq_subnet = requests.get('http://' + cfg.SERVER + '/api/station/subnet/', data={'name': f'{subnet}'})
            subnet_json = json.loads(rq_subnet.text)
            info['station'] = subnet_json['results']['station']
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

    data_file = Path(cfg.DATAFILE)
    checks_data = ConfigParser()

    if data_file.is_file():
        checks_data.read(data_file)
    else:
        checks_data['DATA'] = {
            'mp': False,
            'fp': False,
            'asu': False
        }

    data = checks_data['DATA']
    data['mp'] = str(check_param(host_data, 'check_mp', checks.check_mp()))
    data['fp'] = str(check_param(host_data, 'check_fp', checks.check_fp()))
    data['asu'] = str(check_param(host_data, 'check_asu', checks.check_asu()))
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
    # logger.addHandler(stream_handler)
    logger.info('---------- Run ----------')

    logger.info('> Check updates')
    # if update.update():
    #     logger.info('All scripts up to date')
    # else:
    #     logger.warning('Can\'t update scripts!')

    update_thread = threading.Thread(target=threaded_update, daemon=True)
    update_thread.start()

    logger.info('> Init')

    if client_init.init():
        logger.info('Success setup initial parameters.')
    else:
        logger.warning('Trouble with setup initial parameters.')

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
