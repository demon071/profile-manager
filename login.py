import json
from pathlib import Path
from PyQt5.QtCore import *
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from seleniums import GoLogin
import subprocess
# from selenium import webdriver as uc
import requests

class Login(QThread):

    def __init__(self, profile_id):
        super().__init__()
        self.profile_id = profile_id

    def run(self):
        gl = GoLogin({
            "tmpdir": r'D:\DATA-GOLOGIN\Data', # đường dẫn folder profile
            "local": False,
            "credentials_enable_service": False,
            "extra_params":['--disable-site-isolation-trials'],
            'executablePath': r'C:\Users\DELL\.gologin\browser\orbita-browser-120\chrome.exe'
        })
        gl.setProfileId(self.profile_id)
        params = gl.start()
        cmdCode = " ".join(params)
        subprocess.run(cmdCode, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)