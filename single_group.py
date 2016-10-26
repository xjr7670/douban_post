#!/usr/bin/env python3
#-*- coding:utf-8 -*-
'''
  作于2016年9月26日
  作者：老贤
  本程序主要实现三个功能：
  1. 登录豆瓣（反反爬虫）
  3. 提取指定用户在指定小组中的发言
  由于第3个使用的是豆瓣ID来判断的，而豆瓣ID并不是唯一的
  所有存在一定的误差
  为了方便程序获取页数和翻页，在输入组URL时，要使用以下的形式
    https://www.douban.com/group/gz/discussion?start=0
  以上是首页
  在豆瓣上出现小组链接的地方直接点进去的URL是这样的
    https://www.douban.com/group/gz/
  这时候，点击页面下方的“更多小组讨论”，页面URL就会切换回前面的形式了
'''

import requests
from bs4 import BeautifulSoup as bs
from login import login_douban
from time import sleep

import re


class GetPost(object):

    def __init__(self, session):
        self.session = session
        
        
    def get_post_info(self, user_id, group_url, html_file):
        
        r = self.session.get(group_url)
        
        # 豆瓣有反爬虫机制，会在抓取一段时间后要求输入验证码
        # 此时程序已经被重定向到一个403页面
        
        # 这个功能目前没有实现！！！！！___**___这个if语句块里面的代码是没用的=_=
        if r.status_code == 403:
            # 获取验证码
            preload = dict()
            captcha_bs = bs(r.text, 'html.parser')
            post_form = captcha_bs.find('form', {'action': '/misc/sorry'})
            preload['ck'] = post_form.find(name='ck').attrs['value']
            captcha_url = post_form.find('img', {'alt': 'captcha'}).attrs['src']
            preload['captcha_solution'] = input('输入验证码：%s' % captcha_url)
            preload['captcha_id'] = post_form.find(name='captcha-id').attrs['value']
            preload['original-url'] = page_url
            r = self.session.post('http://www.douban.com/misc/sorry', data=preload)


        html = r.text

        bsObj = bs(html, 'html.parser')

        post_list = bsObj.find('table', {"class": "olt"}).findAll('tr', {'class': ''})
        post_list.pop(0)
        
        for each_post in post_list:
            user_tag = each_post.find('td', {'nowrap': 'nowrap'}).find('a')
            text = user_tag.get_text()

            # 判断是否指定用户所发的贴
            # 如果是则获取帖子链接和标题
            if text == user_id:
                title_tag = each_post.find('td', {'class': 'title'}).find('a')
                url = title_tag.attrs['href']
                title = title_tag.get_text()
                print('发现帖子：%s' % title)

                # 获取发表时间
                time_tag = each_post.find('td', {'class': 'time'})
                time = time_tag.get_text()

                html_str = '<a href="%s" target="_blank">%s</a>\t发表于：%s<br />' % (url, title, time)
                html_file.write(html_str)
                html_file.flush()
            else:
                continue



if __name__ == '__main__':
    
    username = input('输入用户名：')
    password = input('输入密码：')

    # 获取登录后的session
    session = login_douban(username, password)

    # 实例化抓取类，并把会话对象传入
    gp = GetPost(session)

    # 先获取用户ID，方便后面使用
    douban_id = input('输入用户ID：')
    
    group_url = input('输入组链接：')
    r = session.get(group_url)
    html = r.text
    bsObj = bs(html, 'html.parser')

    next_tag = bsObj.find('span', {"class": "next"})
    total_page = next_tag.previous_element.previous_element
    print("该小组共有%s页" % total_page)

    find_num = input('你想查找多少页？默认查找全部') or total_page
    find_num = int(find_num)
    
    html_file = open('post.html', 'a')

    pre_url = re.sub('\d+', '', group_url)

    for i in range(find_num):
        print("正在查找第%d页" % int(i+1))
        url = pre_url + str(i*25)
        try:
            gp.get_post_info(douban_id, url, html_file)
        except:
            print("第%d页查找失败，跳过" % int(i+1))
            continue
        sleep(5)
    else:
        html_file.close()
        print("查找完成！")
