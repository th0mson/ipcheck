#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, subprocess, logging, tempfile
import json
import requests #pip install requests

from ipaddress import ip_address
from datetime import timedelta, datetime
from tgbot import TG_Bot

class IPCheck:
    # default timeout
    daemonTimeoutDefault = 1 #sec
    tgBotTimeoutDefault  = timedelta(seconds=60) #sec
    lastCheckTime = {}
    CurrentIP = {}
    def __init__(self):
        # Log init
        logging.basicConfig(filename = tempfile.gettempdir() + '/' + (os.path.basename(__file__)).split('.')[0] + '.log',
                            level = logging.DEBUG,
                            format = '%(asctime)s %(levelname)s: %(message)s',
                            datefmt = '%Y-%m-%d %I:%M:%S')
        logging.info('Daemon start')

        # Read config
        cfgPath = os.path.dirname(os.path.realpath(__file__)) + '/config.json'

        if os.path.exists(cfgPath):
            with open(cfgPath) as json_data_file:
                cfg = json.load(json_data_file)
        else:
            self.fireNotify('File "config.json" does not exist. Daemon stopped.')
            sys.exit(2)

        # -- Main parameters
        ## Load Telegram Params:
        if 'tg_bot' not in cfg:
            message = 'Is not define Telegram Bot params (tg_bot) in "config.json". Daemon stopped.'
            self.fireNotify(message)
            logging.error(message)
            sys.exit(2)

        if 'tg_bot_token' in cfg['tg_bot']:
            self.tgbot_token = cfg['tg_bot']['tg_bot_token']
        else:
            message = 'Is not define Telegram Bot Token params (tg_bot_token) in "config.json". Daemon stopped.'
            self.fireNotify(message)
            logging.error(message)
            sys.exit(2)

        if 'tg_chanel_id' in cfg['tg_bot']:
            self.tgbot_chanel_id = cfg['tg_bot']['tg_chanel_id']
        else:
            message = 'Is not define Telegram Bot Chat ID params (tg_chanel_id) in "config.json". Daemon stopped.'
            self.fireNotify(message)
            logging.error(message)
            sys.exit(2)

        if 'tg_proxy_socks_host' in cfg['tg_bot']:
            self.tgbot_proxy_socks_host = cfg['tg_bot']['tg_proxy_socks_host']
        else:
            self.tgbot_proxy_socks_host = ""

        if 'tg_proxy_socks_port' in cfg['tg_bot']:
            self.tgbot_proxy_socks_port = cfg['tg_bot']['tg_proxy_socks_port']
        else:
            self.tgbot_proxy_socks_port = ""

        if self.tgbot_proxy_socks_host != "":
#            self.tgbot_proxy_socks = "socks5://{}:{}".format(self.tgbot_proxy_socks_host, self.tgbot_proxy_socks_port)
            self.tgbot_proxy_socks = "{}:{}".format(self.tgbot_proxy_socks_host, self.tgbot_proxy_socks_port)
        else:
            self.tgbot_proxy_socks = ""

        ## Load Site list
        if 'list_sites' not in cfg:
            message = 'Is not define Sites List params (sites_list) in "config.json". Daemon stopped.'
            self.fireNotify(message)
            logging.error(message)
            sys.exit(2)
        else:
            self.ListSites = cfg['list_sites']

        ## Set daemon timeout
        if 'daemon_timeout' in cfg['main']:
            self.daemonTimeout = cfg['main']['daemon_timeout']
        else:
            self.daemonTimeout = self.daemonTimeoutDefault

        ## Set tg_bot timeout for error message
        if 'tg_bot_timeout' in cfg['main']:
            self.tgBotTimeout = timedelta(seconds=cfg['tg_bot']['tg_bot_timeout'])
        else:
            self.tgBotTimeout = self.tgBotTimeoutDefault

        self.myhost = os.uname()[1]

    def fireNotify(self, msg = ''):
        """
        Fire notify action
        """
        TGBot = TG_Bot(self.tgbot_token)
        TGBot.SendMessage(self.tgbot_proxy_socks, self.tgbot_chanel_id, msg)

        logging.info('Called fireNotify()')

    def ErrorNotify(self, site, Message):
        CurrentCheckTime = datetime.now()
        if (site not in self.lastCheckTime):
            self.lastCheckTime[site] = datetime.now()
            self.fireNotify(Message)
        if ((CurrentCheckTime - self.tgBotTimeout) >= self.lastCheckTime[site]):
            self.fireNotify(Message)
            self.lastCheckTime[site] = CurrentCheckTime
        return self

    def getDaemonTimeout(self):
        """
        Get daemon checking timeout
        """
        return self.daemonTimeout

    def getTgBotTimeout(self):
        """
        Get tg bot error message timeout
        """
        return self.tgBotTimeout

    def dataCheck(self, check_data):
        """
        Check current data from content
        """
        try:
           ip_address(check_data)
        except ValueError:
           return False
        else:
           return True

    def check(self, lastCheckTime = None, testStatus = None):
        """
        Checking sources
        """
        logging.info('Called check()')

        ## Checking all site in List from config
        for site in sorted(self.ListSites):
            logging.debug('sourceCheck: %s', self.ListSites[site]['check_url'])
            parser_count = False
            ErrorMessage = 'Hostname: {}%0A{} is broken'.format(self.myhost, self.ListSites[site]['check_url'])

            try:
                ## Get request
                response = requests.get(self.ListSites[site]['check_url'], verify=False, timeout=(3.05, 27))
                ## Check content right
                parser_count = self.dataCheck((response.text).strip())

                # testing
                if testStatus == 'test':
                    self.fireNotify('Hostname: {}%0AService: IPCHECK%0AStatus: INFO%0AMSG:%0ATesting config:%0A - URL = {},%0A - Current IP: {}'.format(os.uname()[1], self.myhost, self.ListSites[site]['check_url'], (response.text).strip()))

                if (site not in self.CurrentIP):
                    self.CurrentIP[site] = ''

                if  parser_count:
                    if ((response.text).strip() not in self.CurrentIP[site]):
                        self.CurrentIP[site] = (response.text).strip()
                        self.fireNotify('Hostname: {}%0ACurrent IP: {}'.format(self.myhost, self.CurrentIP[site]))
                    return self
                else:
                    CurrentCheckTime = datetime.now()
                    if (site not in self.lastCheckTime):
                        self.lastCheckTime[site] = datetime.now()
                        self.fireNotify(message)
                    # send message to telegram with interval from tgBotTimeout variable
                    ErrorMessage += '%0AIP not got'
                    if ((CurrentCheckTime - self.tgBotTimeout) >= self.lastCheckTime[site]):
                        self.fireNotify(ErrorMessage)
                        self.lastCheckTime[site] = CurrentCheckTime

            except requests.exceptions.ReadTimeout:
                ErrorMessage += '\nRead timeout occured'
                print(ErrorMessage)
                self.ErrorNotify(site, ErrorMessage)
            except requests.exceptions.ConnectTimeout:
                ErrorMessage += '\nConnection timeout occured'
                print(ErrorMessage)
                self.ErrorNotify(site, ErrorMessage)
            except requests.exceptions.ConnectionError:
                ErrorMessage += '\nSeems like dns lookup failed..'
                print(ErrorMessage)
                self.ErrorNotify(site, ErrorMessage)
            except requests.exceptions.HTTPError as err:
                ErrorMessage += '\nHTTP Error occured'
                print(ErrorMessage)
                print('Response is: {content}'.format(content=err.response.content))
                self.ErrorNotify(site, ErrorMessage)

        logging.info('End check()')
        return self

if __name__ == '__main__':
    c = IPCheck()
    c.check(testStatus = 'test')
