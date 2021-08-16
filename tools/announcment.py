import requests
import json
import wget
import os
import config as cfg


def get_announcements(id):
    url = 'http://' + cfg.SERVER + '/api/storage/announcements/'
    rq = requests.get(url, data={'id': id})
    url_json = json.loads(rq.text)
    file_list = []
    for j in url_json['results']:
        file_list.append('http://' + cfg.SERVER + j['file'])
    return file_list


def sync_announcements(urls, folder):
    for f in os.listdir(folder):
        path = os.path.join(folder, f)
        os.remove(path)

    for fl in urls:
        wget.download(fl, out=folder)


fl = get_announcements(2)
sync_announcements(fl, 'temp')
