# get system info: ip, mac, hostname

import netifaces
import logging
import os

module_logger = logging.getLogger('main.system_info')


def sys_info():
    info = {}

    iface = filter(lambda str: 'enp' in str, netifaces.interfaces())
    iface = list(iface)

    mac = netifaces.ifaddresses(iface[0])[netifaces.AF_LINK][0]['addr']
    ip = netifaces.ifaddresses(iface[0])[netifaces.AF_INET][0]['addr']
    hostname = os.uname()[1]
    info['ip'] = ip
    info['mac'] = mac
    info['hostname'] = hostname

    return info
