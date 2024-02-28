import json
import requests
from PyQt5.QtCore import *
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from pathlib import Path



class ScanPage(QObject):
    sign_exit = pyqtSignal()
    sign_data = pyqtSignal(list)
    def __init__(self, listAccount):
        super().__init__()
        self.listAccount = listAccount
        self.driver = None

    def run(self):
        for acc in self.listAccount:
            cookie = acc['cookie']
            token = acc['token']
            userId = acc['userId']
            userAgent = acc['userAgent']
            profile = acc['profile']
            self.scan(cookie=cookie, token=token, userAgent=userAgent, userId=userId, profile=profile)
        self.sign_exit.emit()

    
    def scan(self, cookie, token, userId, userAgent, profile):
        url = 'https://graph.facebook.com/me/accounts?access_token='+ token
        try:
            options = uc.ChromeOptions()
            options.add_argument('--user-data-dir='+profile)
            # from webdriver_manager.core.utils import ChromeType, get_browser_version_from_os
            # ver = get_browser_version_from_os(ChromeType.GOOGLE).split('.')[0]
            # options.set_capability("detach", True)
            path = str(Path().absolute())
            binary_location = path + "\\GoogleChromePortable\\App\\Chrome-bin\\chrome.exe"
            chromedriver = path + '\\chromedriver.exe'
            # from webdriver_manager.core.utils import ChromeType, get_browser_version_from_os
            # ver = get_browser_version_from_os(ChromeType.GOOGLE).split('.')[0]
            # options.set_capability("detach", True)
            self.driver = uc.Chrome(options=options, use_subprocess=True, browser_executable_path=binary_location, driver_executable_path=chromedriver)
            # self.driver = uc.Chrome(options=options, use_subprocess=True, version_main=ver)
            while True:
                try:
                    self.driver.get('https://www.facebook.com/')
                    break
                except:
                    continue
            # self.sign_chrome.emit(True)
            cookies = self.driver.get_cookies()
            cookie = ["=".join([x['name'], x['value']]) for x in cookies]
            strCookie = ";".join(cookie)
            if 'c_user' not in strCookie:
                self.driver.close()
                self.driver.quit()
                print('tai khong khong dang nhap')
                return False
        except:
            self.driver = None
        
        if self.driver != None:
            while True:
                try:
                    print('in ne')
                    self.driver.get(url)
                    
                    break
                except:
                    continue
            try:
                import time 
                time.sleep(5)
                html = self.driver.find_element(By.TAG_NAME, 'body').text
                userAgent = self.driver.execute_script('return window.navigator.userAgent')
                dl = json.loads(html)

                data = dl['data']
                list_page = []
                if len(data):
                    for x in data:
                        list_page.append({
                            'token': x['access_token'],
                            'userId': x['id'],
                            'username': x['name'], 
                            'cookie': strCookie,
                            'userAgent': userAgent,
                            'platform': 'Page',
                            'fanpageOfUser': userId,
                        })
                    # print(list_page)
                    self.sign_data.emit(list_page)
            except Exception:
                import traceback
                print(traceback.format_exc())
                pass
        
            self.driver.close()
            self.driver.quit()
            self.driver = None
        
        
        
