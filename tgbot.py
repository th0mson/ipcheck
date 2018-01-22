#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import json
import requests #pip install requests

class TG_Bot:
    def __init__(self, token):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)

    def SendMessage(self, Chanel_ID, Message):
        params = {'chat_id': Chanel_ID, 'text': Message}
        method = 'sendMessage'
        response = requests.post(self.api_url + method, params)
        return response

# Test function
def TGBot_Test():
    # read config
    cfgPath = os.path.dirname(os.path.realpath(__file__)) + '/config.json'

    if os.path.exists(cfgPath):
        with open(cfgPath) as json_data_file:
            cfg = json.load(json_data_file)
    else:
        print('Config file not found')

    if 'tg_bot' not in cfg:
        print('Not define tg_bot params in config.json. Script exist')
        sys.exit(0)

    if 'tg_bot_token' in cfg['tg_bot']:
        tgbot_token = cfg['tg_bot']['tg_bot_token']
    else:
        print('Not define tg_bot_token in config.json. Script exist')
        sys.exit(2)

    if 'tg_chanel_id' in cfg['tg_bot']:
        tgbot_chanel_id = cfg['tg_bot']['tg_chanel_id']
    else:
        print('Not define tg_chanel_id in config.json. Script exist')
        sys.exit(2)

    TGBot = TG_Bot(tgbot_token)
    TGBot.SendMessage(tgbot_chanel_id, 'test message')

if __name__ == '__main__':
    TGBot_Test()
