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

    r = session.get('https://www.douban.com/accounts/login')
    # 豆瓣有反爬虫机制，会在抓取一段时间后要求输入验证码
    # 此时程序已经被重定向到一个403页面
    test_html = r.text
    test_bo = BeautifulSoup(test_html, 'lxml')
    print(test_html)
    title = test_bo.title.string
    if title == '禁止访问':
        # 获取验证码
        preload = dict()
        captcha_bs = BeautifulSoup(r.text, 'lxml')
        post_form = captcha_bs.find('form', {'action': '/misc/sorry'})
        preload['ck'] = post_form.find(name='ck').attrs['value']
        captcha_url = post_form.find('img', {'alt': 'captcha'}).attrs['src']
        preload['captcha_solution'] = input('输入验证码：%s' % captcha_url)
        preload['captcha_id'] = post_form.find(name='captcha-id').attrs['value']
        preload['original-url'] = page_url
        r = self.session.post('http://www.douban.com/misc/sorry', data=preload)

    html = r.text
    bsObj = BeautifulSoup(html, 'lxml')

    # get captcha and captcha id
    try:
        cap = bsObj.find('img', {'id': 'captcha_image'})
        captcha_url = cap.attrs['src']
        captcha = input('Please input the captcha code %s :' % captcha_url)
        preload['captcha-solution'] = captcha

        cap_id = bsObj.find('input', {'name': 'captcha-id'})
        captcha_id = cap_id.attrs["value"]
        preload['captcha-id'] = captcha_id
    except Exception as e:
        print('不需要验证码。', e)


    main_page = session.post(login_url, headers=headers, data=preload)
    t = session.get('https://www.douban.com/people/92549523/')
    try:
        main_page.raise_for_status()
    except Exception as e:
        print('登录失败！', e)
        return None
    return session

if __name__ == '__main__':
    login_douban('xjr30226@126.com', 'x45668668')
