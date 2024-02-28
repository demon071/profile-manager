import os
import pathlib
import random
import json
import time
import sys
import subprocess
import tempfile
from sys import platform
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
# from extensionsManager import *
import requests
import socket

def getRandomPort():
    while True:
        port = random.randint(1000, 35000)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        if result == 0:
            continue
        else:
            return port
        sock.close()

class GoLogin(object):
    def __init__(self, options):
        self.tmpdir = options.get('tmpdir', tempfile.gettempdir())
        self.address = options.get('address', '127.0.0.1')
        self.extra_params = options.get('extra_params', [])
        self.port = options.get('port', 3500) #port mặc định
        self.local = options.get('local', False)
        self.spawn_browser = options.get('spawn_browser', True)
        self.credentials_enable_service = options.get('credentials_enable_service')

        home = str(pathlib.Path.home())
        self.executablePath = options.get('executablePath', 'gologin\\browser\\orbita-browser-105\chrome.exe') #Orbita Path
        if not os.path.exists(self.executablePath) and sys.platform == "darwin":
            self.executablePath = os.path.join(home, '.gologin/browser/Orbita-Browser.app/Contents/MacOS/Orbita')
        if self.extra_params:
            print('extra_params', self.extra_params)
        self.setProfileId(options.get('profile_id'))

    def setProfileId(self, profile_id):
        self.profile_id = profile_id
        if self.profile_id == None:
            return
        self.profile_path = os.path.join(self.tmpdir, self.profile_id)


    def spawnBrowser(self, Proxy):
        self.port = getRandomPort()
        proxy = ''
        proxy_host = ''
        username = ''
        password = ''
        try:
            schema = Proxy.split('://')[0]
            proxies = Proxy.split('://')[1].split(':')
            proxy_host = proxies[0]
            port = proxies[1]
            proxy= f"{proxy_host}:{port}"
        except Exception as re:
            print(re)

        params = [
            self.executablePath,
            '--user-data-dir=' + self.profile_path,
            '--password-store=basic',
            '--lang=en',
        ]
        # print(proxy)
        if proxy:
            hr_rules = '"MAP * 0.0.0.0 , EXCLUDE %s"' % (proxy_host)
            params.append('--proxy-server=' + proxy)
            params.append('--host-resolver-rules=' + hr_rules)

        for param in self.extra_params:
            params.append(param)
        # print(params)
        return params
        # subprocess.Popen(params, start_new_session=True, shell=True)
        # try_count = 1
        # url = str(self.address) + ':' + str(self.port)

        # while try_count<100:
        #     try:
        #         data = requests.get('http://'+url+'/json').content
        #         break
        #     except:
        #         try_count += 1
        #         time.sleep(1)
        # return url

    def start(self, Proxy = None):
        profile_path = os.path.join(self.tmpdir, self.profile_id)
        # print(profile_path)
        if self.spawn_browser == True:
            return self.spawnBrowser(Proxy)
        return profile_path

    def Change_Proxy(self,Proxy):
        schema = host = port = username = password = ''
        if Proxy:
            username = ''
            password = ''
            try:
                schema = Proxy.split('://')[0]
                host_port = Proxy.split('://')[1].split(':')
                host = host_port[0]
                port = host_port[1]
                if len(host_port) == 4:
                    username = host_port[2]
                    password = host_port[3]

                # print(schema)
            except Exception as re:
                print(re)

            with open(f"{self.profile_path}\\Default\\Preferences", 'r', encoding="utf8") as aa:
                data_profile = json.load(aa)
                data_profile['gologin']['proxy'] = {
                    "id": None,
                    "mode": schema,
                    "host": host,
                    "port": port,
                    "username": username,
                    "password": password,
                    "changeIpUrl": str('null'),
                    "autoProxyRegion": "us",
                    "torProxyRegion": "us"
                }
                if data_profile:
                    pfile = open(f"{self.profile_path}\\Default\\Preferences", 'w')
                    json.dump(data_profile, pfile)
                    pfile.close()
    def waitDebuggingUrl(self, delay_s, try_count=3):
        url = 'https://' + self.profile_id + '.guidevn.com/json/version'
        wsUrl = ''
        try_number = 1
        while wsUrl == '':
            time.sleep(delay_s)
            try:
                response = json.loads(requests.get(url).content)
                wsUrl = response.get('webSocketDebuggerUrl', '')
            except:
                pass
            if try_number >= try_count:
                return {'status': 'failure', 'wsUrl': wsUrl}
            try_number += 1

        wsUrl = wsUrl.replace('ws://', 'wss://').replace('127.0.0.1', self.profile_id + '.guidevn.com')
        return {'status': 'success', 'wsUrl': wsUrl}

    def formatProxyUrl(self, proxyzz):
        return proxyzz.get('mode', 'http') + '://' + proxyzz.get('host', '') + ':' + str(proxyzz.get('port', 80))

    def formatProxyUrlPassword(self, proxyzz):
        
        if proxyzz.get('username', '') == '':
            return proxyzz.get('mode', 'http') + '://' + proxyzz.get('host', '') + ':' + str(
                proxyzz.get('port', 80))
        else:
            return proxyzz.get('mode', 'http') + '://' + proxyzz.get('username', '') + ':' + proxyzz.get(
                'password') + '@' + proxyzz.get('host', '') + ':' + str(proxyzz.get('port', 80))

    def getTimeZone(self,):
        with open(f"{self.profile_path}\\Default\\Preferences", 'r') as f:
            data_profile = json.load(f)
            modes = data_profile['gologin']['proxy']['mode']
            hosts = data_profile['gologin']['proxy']['host']
            ports = data_profile['gologin']['proxy']['port']
            try:
                username = data_profile['gologin']['proxy']['username']
                password = data_profile['gologin']['proxy']['password']
            except:
                username = ''
                password = ''

            if (modes == "none"):
                proxyzz = None
            elif (modes == "socks5"):
                proxyzz = {
                    'mode': 'socks5h',
                    'host': hosts,
                    'port': ports,
                    'username': username,
                    'password': password
                }
            elif (username == None):
                proxyzz = {
                    'mode': modes,
                    'host': hosts,
                    'port': ports,
                    'username': username,
                    'password': password
                }
            elif (username == 'Null'):
                proxyzz = {
                    'mode': modes,
                    'host': hosts,
                    'port': ports,
                    'username': username,
                    'password': password
                }
            else:
                proxyzz = data_profile['gologin']['proxy']
        # print(proxyzz)
        headers = {
            'User-Agent': 'gologin-api'
        }
        if proxyzz:
            proxies = dict(
                http=self.formatProxyUrlPassword(proxyzz),
                https=self.formatProxyUrlPassword(proxyzz)
            )
            print(proxies)
            data = requests.get('https://geo.myip.link', proxies=proxies, headers=headers)
        else:
            data = requests.get('https://geo.myip.link')
        return json.loads(data.content.decode('utf-8'))

    def update(self,profile_id):
        self.tz = self.getTimeZone()
        self.ChangeTimezone()
    def ChangeTimezone(self):
        ips = self.tz.get('ip')
        timezons = self.tz.get('timezone')
        # print(timezons)
        try:
            with open(f"{self.profile_path}\\Default\\Preferences", 'r') as q:
                preferences = json.load(q)
                preferences['gologin']['webRTC']['publicIp'] = ips
                preferences['gologin']['webRtc']['publicIP'] = ips
                preferences['gologin']['webRtc']['public_ip'] = ips
                preferences['gologin']['timezone']['id'] = timezons

                preferences['gologin']['geoLocation']['latitude'] = self.tz.get('ll', [0, 0])[0]
                preferences['gologin']['geoLocation']['longitude'] = self.tz.get('ll', [0, 0])[1]
                preferences['gologin']['geoLocation']['accuracy'] = self.tz.get('accuracy', 0)

                preferences['gologin']['geolocation']['latitude'] = self.tz.get('ll', [0, 0])[0]
                preferences['gologin']['geolocation']['longitude'] = self.tz.get('ll', [0, 0])[1]
                preferences['gologin']['geolocation']['accuracy'] = self.tz.get('accuracy', 0)
                q.close()
                if preferences:
                    pfiles = open(f"{self.profile_path}\\Default\\Preferences", 'w')
                    json.dump(preferences, pfiles)
                    pfiles.close()
        except Exception as e:
            print('loi time zone')
            print(e)


# Khởi chạy Profile offline

# gl = GoLogin({
#     "tmpdir": r'D:\DATA-GOLOGIN\Data', # đường dẫn folder profile
#     "local": False,
#     "credentials_enable_service": False,
#     "port": random.randint(10000, 50000),
#     "extra_params":['--disable-site-isolation-trials'],
#     'executablePath': r'C:\Users\DELL\.gologin\browser\orbita-browser-120\chrome.exe'
# })
# Proxy = None

# # 87.248.131.178:50100:Selmacnghia191090:B6x3OqJ
# # 45.149.154.102:50100:Selmacnghia191090:B6x3OqJ

# Proxy_data = ['http://87.248.131.178:50100:Selmacnghia191090:B6x3OqJ','http://45.149.154.102:50100:Selmacnghia191090:B6x3OqJ']
# Proxy_data = []
# if Proxy_data:
#     for Proxy_new in Proxy_data:
#         Proxy = Proxy_new

# profile_id = '65386a633955131ecdfe2f57'
# gl.setProfileId(profile_id)
# if Proxy:
#     gl.Change_Proxy(Proxy)
#     gl.update(profile_id)


# print('profile start: ', profile_id)
# print('Proxy start: ', Proxy)
# debugger_address = gl.start()
# print(debugger_address)
# chrome_options = Options()
# chrome_driver_path = Service(ChromeDriverManager().install())
# chrome_options.add_experimental_option("debuggerAddress", debugger_address)
# driver = webdriver.Chrome(service=chrome_driver_path, options=chrome_options)
# driver.get("https://www.tiktok.com/search/video?q=football")

# time.sleep(2)
# loginBox = driver.find_element(By.ID, 'identifierId')
# loginBox.send_keys('huongthuy70483')
# time.sleep(2)
# loginBox.send_keys(Keys.ENTER)

# time.sleep(2)
# passWordBox = driver.find_element(By.NAME, 'Passwd')
# passWordBox.send_keys('0951@a1a')
# time.sleep(2)
# passWordBox.send_keys(Keys.ENTER)



