#! /usr/bin/python3

from json.decoder import JSONDecodeError
import logging
import json
import requests
import config as cfg
import netifaces
import os
import time
import tools

from pathlib import Path
from configparser import ConfigParser

online = False


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


def loop():
    global online
    host_data = {}
    if tools.check_alive():
        if not online:
            logging.info('Host online.')
            online = True

        rq_data = tools.sys_info()

        try:
            rq = requests.get('http://' + cfg.SERVER + '/api/host/', data=rq_data)
        except ConnectionError:
            logging.error(f'{ ConnectionError.strerror }')

        try:
            host_data = json.loads(rq.text)
        except JSONDecodeError:
            host_data = {}

        if rq.status_code == 400:
            logging.warning('Host not registered, try to register')

            info = tools.sys_info()
            ip = info['ip']
            subnet = ip.replace(ip[ip.rfind('.') + 1:len(ip)], '0/24')
            rq_subnet = requests.get('http://' + cfg.SERVER + '/api/station/subnet/', data={'name': f'{subnet}'})
            subnet_json = json.loads(rq_subnet.text)
            info['station'] = subnet_json['results']['station']
            if tools.register(info):
                logging.debug('Registration successfull!')
            else:
                logging.error('Registration error!')

        if rq.status_code == 200:
            logging.info('Host alredy registered, checking ssh tunnel')
            tunnel_up = tools.tunnel_check(host_data['ssh'], host_data['vnc'])
            if tunnel_up:
                logging.info('SSH tunnel is up.')
            else:
                logging.warning('SSH tunnel have problem!')

            send_json = {'id': host_data['pk']}
            logging.info('Try to touch server...')
            rq_touch = requests.post('http://' + cfg.SERVER + '/api/touch/', data=send_json)
            if rq_touch.status_code == 200:
                logging.info('Server touched.')
            else:
                logging.warning('Can\'t touch server!')
    else:
        if online:
            logging.warning('Host offline!')
            online = False

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

    logging.info('> Matrix printer')

    data['mp'] = str(check_param(host_data, 'check_mp', tools.mp_check()))
    logging.debug(f'Matrix printer check result: {data["mp"]}')

    logging.info('> Fiscal printer')
    data['fp'] = str(check_param(host_data, 'check_fp', tools.fp_check()))
    logging.debug(f'Fiscal printer check result: {data["fp"]}')

    logging.info('> Server ASU')
    data['asu'] = str(check_param(host_data, 'check_asu', tools.asu_check()))
    logging.debug(f'Server check result: {data["asu"]}')

    checks_data['DATA'] = data
    with open(data_file, 'w') as conf:
        checks_data.write(conf)


def main():
    logging.basicConfig(
        filename='/var/log/kat_client.log',
        format='%(asctime)s %(levelname)s: %(message)s',
        level=logging.INFO
    )
    logging.info('---------- Run ----------')
    logging.info(f'> log level: {logging.root.level}')

    logging.info('> Check updates')
    if tools.update():
        logging.info('All scripts up to date')
    else:
        logging.warning('Can\'t update scripts!')

    logging.info('> Init')
    if tools.init():
        logging.info('Success setup initial parameters.')
    else:
        logging.warning('Trouble with setup initial parameters.')

    while True:
        start_time = time.time()
        loop()
        time.sleep(5)
        logging.debug(f'Execution time: {time.time() - start_time}')


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('\nExit program')
        os._exit(0)
