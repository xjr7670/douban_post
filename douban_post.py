#!/usr/bin/env python3
#-*- coding:utf-8 -*-
'''
  作于2016年9月26日
  作者：老贤
  本程序主要实现三个功能：
  1. 登录豆瓣（反反爬虫）
  2. 提取指定用户所加入的所有小组的链接
  3. 提取指定用户在指定小组中的发言
  由于第3个使用的是豆瓣ID来判断的，而豆瓣ID并不是唯一的
  所有存在一定的误差
'''

import time
import requests
from bs4 import BeautifulSoup as bs
from login import login_douban


class GetPost(object):

    def __init__(self, session):
        self.session = session
        
        
    def get_group_list(self, joined_url):
        r = self.session.get(joined_url)
        html = r.text
        bsObj = bs(html, 'lxml')
        
        # 查找结果将保存在group_list列表中
        group_list = []
        group_dict = dict()

        gs = bsObj.findAll('div', {'class': 'group-list group-cards'})
        assert len(gs) >= 1, print(html)
        if len(gs) == 2:
            li_tags = gs[1].findAll('li')
        else:
            li_tags = gs[0].findAll('li')
        for each_li in li_tags:
            title_div = each_li.find('div', {"class": "title"}).find('a')
            title = title_div.attrs['title']
            url = title_div.attrs['href']
            group_list.append(url)
            group_dict[url] = title

        return (group_list, group_dict)
    
    def get_post_info(self, page_url, user_id, html_file):
        
        r = self.session.get(page_url)
        
        # 豆瓣有反爬虫机制，会在抓取一段时间后要求输入验证码
        # 此时程序已经被重定向到一个403页面
        if r.status_code == 403:
            # 获取验证码
            preload = dict()
            captcha_bs = bs(r.text, 'lxml')
            post_form = captcha_bs.find('form', {'action': '/misc/sorry'})
            preload['ck'] = post_form.find(name='ck').attrs['value']
            captcha_url = post_form.find('img', {'alt': 'captcha'}).attrs['src']
            preload['captcha_solution'] = input('输入验证码：%s' % captcha_url)
            preload['captcha_id'] = post_form.find(name='captcha-id').attrs['value']
            preload['original-url'] = page_url
            r = self.session.post('http://www.douban.com/misc/sorry', data=preload)


        html = r.text

        bsObj = bs(html, 'lxml')
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

    # 获取指定用户所加入的所有小组的连接
    # 需要人工打开该用户的主页并找到其所加入的小组的页面URL
    # 将其传入对应的类方法中
    # 返回一个列表
    joined_group_url = input('输入该用户加入的小组页面URL：')
    group_url_list, group_url_dict = gp.get_group_list(joined_group_url)

    # 显示该用户共加入了多少个小组
    # 以方便只在TA最活跃的N个小组中的发言
    group_num = len(group_url_list)
    print('该用户共加入了%s个小组' % group_num)

    # 指定查询多少个小组
    num = int(input('你想查询多少个小组（数量应在0－%s之间)：' % group_num))

    # 限定查询的页数
    page_num = int(input('你想在各小组中查询多少页：'))

    # 用两个循环
    # 外循环用于历遍小组链接
    # 内循环用于历遍组内各页面

    # 根据用户ID查找其所发表的帖子
    # 并将标题和发表时间一起写到一个HTML文件中
    html_file = open('post.html', 'a', encoding='utf-8')

    for i in range(num):
        print('正在查询第%s个小组：%s' % (str(i+1), group_url_dict[group_url_list[i]]))
        for j in range(page_num):
            print('\t正在查找第%s页' % str(j+1))
            url = group_url_list[i] + 'discussion?start=' + str(25 * j)
            

            # 执行查找
            try:
                gp.get_post_info(url, douban_id, html_file)
            except Exception e:
                print(str(e))
                pass

            time.sleep(1)

    else:
        html_file.close()
        print('查找完成！')
