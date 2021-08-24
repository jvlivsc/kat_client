import requests
import json
# import config as cfg
import subprocess


def get_announcements(id):
    # url = 'http://' + cfg.SERVER + '/api/storage/announcements/'
    url = 'http://' + '10.2.3.55' + '/api/storage/announcements/'
    file_list = []
    try:
        rq = requests.get(url, data={'id': id})
        url_json = json.loads(rq.text)
        for j in url_json['results']:
            # file_list.append('http://' + cfg.SERVER + j['file'])
            file_list.append('http://' + '10.2.3.55' + j['file'])
    except requests.ConnectionError as e:
        print(e.strerror)

    return file_list


def sync_announcements(urls, folder):
    for u in urls:
        result = subprocess.run(['wget', '-m', u, '-nd', '-P', folder], capture_output=True)
        print(result.returncode)
        if result.returncode == 0:
            return True

    return False

# fl = get_announcements(2)
# sync_announcements(fl, 'temp')
