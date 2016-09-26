#!/usr/bin/python3
#-*- coding:utf-8 -*-

import requests
from bs4 import BeautifulSoup

def login_douban(username, password):
    session = requests.Session()
    login_url = "https://accounts.douban.com/login"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36',
    }

    preload = {
        'source': 'None',
        'redir': 'https://www.douban.com/people/92549523/',
        'form_email': username,
        'form_password': password,
        'remember': 'on',
        'login': u'登录'
        }

    # get captcha and captcha id
    try:
        cap = bsObj.find('img', {'id': 'captcha_image'})
        captcha_url = cap.attrs['src']
        captcha = input('Please input the captcha code %s :' % captcha_url)
        preload['captcha-solution'] = captcha

        cap_id = bsObj.find('input', {'name': 'captcha-id'})
        captcha_id = cap_id.attrs["value"]
        preload['captcha-id'] = captcha_id
    except:
        pass


    main_page = session.post(login_url, headers=headers, data=preload)
    return session

if __name__ == '__main__':
    login_douban(username, password)
