# -*- coding: utf-8 -*-
import requests
import time
import socket

import xml.etree.ElementTree as ET


URL = 'https://api.telegram.org/bot'  # HTTP Bot API URL
INTERVAL = 0.5


def get_token():
    tree = ET.parse('private_config.xml')
    root = tree.getroot()
    token = root.findall('token')[0].text
    return token


def get_admin():
    tree = ET.parse('private_config.xml')
    root = tree.getroot()
    admin_id = root.findall('admin_id')[0].text
    return admin_id


def get_proxies():
    tree = ET.parse('private_config.xml')
    root = tree.getroot()
    proxy_url = root.findall('proxy')[0].text
    proxies = {
        "http": proxy_url,
        "https": proxy_url,
    }
    return proxies


def check_mode():
    import requests

    try:
        requests.get('https://www.ya.ru')
        return False
    except:
        proxies = get_proxies()
        requests.get('https://www.ya.ru', proxies=proxies)
        return True


class Telegram:
    def __init__(self):
        self.proxy = check_mode()
        self.TOKEN = get_token()
        self.URL = 'https://api.telegram.org/bot'
        if self.proxy:
            self.proxies = get_proxies()
        self.admin_id = get_admin()
        self.offset = 0
        self.host = socket.getfqdn()
        self.Interval = INTERVAL
        if not self.proxy:
            log_event("Init completed, host: " + str(self.host))
        if self.proxy:
            log_event("Init completed with proxy, host: " + str(self.host))

    def get_updates(self):
        data = {'offset': self.offset + 1, 'limit': 5, 'timeout': 0}
        if not self.proxy:
            request = requests.post(self.URL + self.TOKEN + '/getUpdates', data=data)
        if self.proxy:
            request = requests.post(self.URL + self.TOKEN + '/getUpdates', data=data, proxies=self.proxies)
        if (not request.status_code == 200) or (not request.json()['ok']):
            return False

        if not request.json()['result']:
            return
        updates_list = []
        for update in request.json()['result']:
            self.offset = update['update_id']

            if 'message' not in update or 'text' not in update['message']:
                continue

            from_id = update['message']['chat']['id']  # Chat ID
            author_id = update['message']['from']['id']  # Creator ID
            message = update['message']['text']
            date = update['message']['date']
            try:
                name = update['message']['chat']['first_name']
            except:
                name = update['message']['from']['first_name']
            parameters = (name, from_id, message, author_id, date)
            updates_list.append(parameters)
            try:
                log_event('from %s (id%s): "%s" with author: %s; time:%s' % parameters)
            except:
                pass
        return updates_list

    def send_text_with_keyboard(self, chat_id, text, keyboard):
        try:
            log_event('Sending to %s: %s; keyboard: %s' % (chat_id, text, keyboard))  # Logging
        except:
            log_event('Error with LOGGING')
        json_data = {"chat_id": chat_id, "text": text,
                     "reply_markup": {"keyboard": keyboard, "one_time_keyboard": True}}
        if not self.proxy:  # no proxy
            request = requests.post(self.URL + self.TOKEN + '/sendMessage', json=json_data)  # HTTP request

        if self.proxy:
            request = requests.post(self.URL + self.TOKEN + '/sendMessage', json=json_data,
                                    proxies=self.proxies)  # HTTP request with proxy

        if not request.status_code == 200:  # Check server status
            return False
        return request.json()['ok']  # Check API

    def send_photo(self, chat_id, imagePath):
        try:
            log_event('Sending photo to %s: %s' % (chat_id, imagePath))  # Logging
        except:
            log_event('Error with LOGGING')
        data = {'chat_id': chat_id}
        files = {'photo': (imagePath, open(imagePath, "rb"))}
        requests.post(self.URL + self.TOKEN + '/sendPhoto', data=data, files=files)

    def send_text(self, chat_id, text):
        try:
            log_event('Sending to %s: %s' % (chat_id, text))  # Logging
        except:
            log_event('Error with LOGGING')
        data = {'chat_id': chat_id, 'text': text}  # Request create
        if not self.proxy:
            request = requests.post(self.URL + self.TOKEN + '/sendMessage', data=data)  # HTTP request

        else:
            request = requests.post(self.URL + self.TOKEN + '/sendMessage', data=data,
                                    proxies=self.proxies)  # HTTP request with proxy

        if not request.status_code == 200:  # Check server status
            return False
        return request.json()['ok']  # Check API


def log_event(text):
    f = open('log.txt', 'a')
    event = '%s >> %s' % (time.ctime(), text)
    print event + '\n'
    f.write(event + '\n')
    f.close()
    return