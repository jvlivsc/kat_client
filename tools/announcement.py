from posix import listdir
import requests
import json
import config as cfg
import subprocess
import os


def get_announcements(id):
    url = 'http://' + cfg.SERVER + '/api/storage/announcements/'
    file_list = []
    try:
        rq = requests.get(url, data={'id': id})
        url_json = json.loads(rq.text)
        if url_json['success']:
            for j in url_json['results']:
                file_list.append('http://' + cfg.SERVER + j['file'])
        else:
            print(url_json['results'])
    except requests.ConnectionError as e:
        print(e.strerror)

    return file_list


def sync_announcements(urls, folder):
    dir = cfg.AUDIO_PATH
    files = os.listdir(dir)
    files_to_rm = [file for file in files if not any(file in url for url in urls)]
    for file in files_to_rm:
        os.remove(os.path.join(dir, file))

    for u in urls:
        wget = subprocess.run(['wget', '-m', u, '-nd', '-P', folder], capture_output=True)

    return wget
