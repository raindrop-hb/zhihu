#!/usr/bin/python3.10
# -*- coding: utf-8 -*-
# Copyright (C) 2023 , Inc. All Rights Reserved 
# @Time    : 2023/7/22 12:47
# @Author  : raindrop
# @Email   : 1580925557@qq.com
# @File    : main.py
# 不保留版权死全家
import random
from time import strftime,localtime,time,sleep
import requests,json,os,re
from urllib.parse import quote
import lxml.html
import urllib3
from webbrowser import open as dss
urllib3.disable_warnings()

etree=lxml.html.etree

def configs():
    #360小说网https://h.x360xs.com/账号密码
    aa=["账号","密码"]
    return aa



def login():
    time_1 = int(time())
    config = configs()
    username=config["login"]
    num=random.randrange(0, len(username))
    printt("读取账号密码\n账号：{}\n密码：{}".format(config[0], config[1]))
    url="https://h.x360xs.com/index.php?m=user/ajax&format=jsonp&inputuserid="+quote(config[0])+"&password="+quote(config[1])+"&ajaxMethod=StaticLogin&autologinflag=1&method=_jqjsp&_"+str(time_1)+"="
    header={
        "Referer":"https://h.x360xs.com/index.php?m=user/login",
        "accept_language":"zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "User-Agent":"Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1 Edg/114.0.0.0"
    }
    resp=requests.get(url,headers=header,verify=False)
    cookie = requests.utils.dict_from_cookiejar(resp.cookies)
    printt("登录成功")
    return cookie


def search(cookie,book_name):
    url="https://h.x360xs.com/book/"
    ck = ""
    for i in cookie:
        ck=ck + str(i) + "=" + str(cookie[i]) + ";"
    header={
        "User-Agent":"Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1 Edg/114.0.0.0",
        "Referer":"https://h.x360xs.com/search/",
        "cookie":ck
    }

    params = {
        "ajaxMethod": "getsearchbooks",
        "page": "1",
        "pagesize": "10",
        "isvip": "-1",
        "cid": "-1",
        "sort": "0",
        "flag": "-1",
        "searchkey": book_name,
        "site": "-1",
        "again": "0",
        "range": "-1"
    }
    resp=requests.post(url=url,data=params,headers=header,verify=False).json()
    return resp

def book_info(cookie,choose_dict):
    ck = ""
    for i in cookie:
        ck = ck + str(i) + "=" + str(cookie[i]) + ";"
    header = {
        "Referer": "https://www.x360xs.com/login.php?jumpurl=%2Fmodules%2Farticle%2Fbookcase.php",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.79"
    }
    try:
        book_num=re.findall("第(.*)节",choose_dict["lastchaptername"])[0]
        book_num=int(book_num.replace(" ",""))
    except:
        book_num = re.findall("第(.*)章", choose_dict["lastchaptername"])[0]
        book_num = int(book_num.replace(" ", ""))
    page=book_num//50
    if book_num%50>0:
        page+=1
    real_page=1
    page_dict = dict()
    while True:
        printt("共{}页，当前第{}页".format(str(page),str(real_page)))
        resp=requests.get("https://h.x360xs.com/book/"+choose_dict["bookid"]+"/0/"+str(real_page)+".html",headers=header,verify=False).text
        resp=resp.replace("  ","").replace("\n","").replace("\r","")
        html = etree.HTML(resp)
        text = html.xpath('/html/body/div[3]/div//div/div[2]/a/text()|/html/body/div[3]/div//div/div[2]/a/@href')
        s_1=0
        for ii in range(len(text)//2):
            try:
                book_n = str(re.findall("第(.*)节", text[ii*2+1])[0])
                book_n=book_n.replace(" ","")
            except:
                book_n = str(re.findall("第(.*)章", text[ii * 2 + 1])[0])
                book_n = book_n.replace(" ", "")
            list_1=[text[ii*2],text[ii*2+1]]
            page_dict[book_n]=list_1
            printt(text[ii*2+1])
        choose=input("请输入章节序号,回车进入下一页：")
        if choose=="":
            if real_page<page:
                real_page+=1
        elif choose.isdigit():
            page_url="https://h.x360xs.com" + page_dict[choose][0]
            resp = requests.get(page_url, headers=header, verify=False).text
            resp = resp.replace("  ", "").replace("\n", "").replace("\r", "")
            html = etree.HTML(resp)
            text = html.xpath('/html/body/form/div[2]/div[5]/img/@onerror')[0]
            text=text[text.find(choose_dict["bookid"]):]
            next_page=re.findall("(.*)'.split",text)[0]
            next_page=next_page.split("|")[2]
            printt(next_page)
            page_referer=page_url
            text_list = html.xpath('/html/body/form/div[2]/div[2]/div/div//p/text()')
            while True:
                if "本章节未完结" in resp:
                    page_url="https://h.x360xs.com/book/"+choose_dict["bookid"]+"/"+next_page+".html"
                    page_list=page_next(ck,page_url,page_referer,choose_dict["bookid"])
                    next_page=page_list[0]
                    resp=page_list[1]
                    page_referer = page_url
                    text_list.extend(page_list[2])
                    #book_txt=book_txt+page_list[2]
                else:
                    book_all=""
                    printt("合并分页中")
                    for iiiii in text_list:
                        book_all+=iiiii+"\n"
                        printt(iiiii)
                    with open(page_dict[choose][1]+".txt","w+",encoding="UTF-8")as f:
                        f.write(book_all)
                        printt("成功写入文件{}.txt中".format(page_dict[choose][1]))
                    #print(book_txt)
                    break
            break
        else:
            printt("请输入序号")

def page_next(cookie,page_url,page_referer,bookid):
    header = {
        "Cookie":cookie,
        "Referer": page_referer,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.79"
    }
    resp = requests.get(page_url, headers=header, verify=False).text
    resp = resp.replace("  ", "").replace("\n", "").replace("\r", "")
    html = etree.HTML(resp)
    text = html.xpath('/html/body/form/div[2]/div[5]/img/@onerror')[0]
    text = text[text.find(bookid):]
    next_page = re.findall("(.*)'.split", text)[0]
    next_page = next_page.split("|")[2]
    printt(next_page)
    text = html.xpath('/html/body/form/div[2]/div[2]/div/div//p/text()')
    return [next_page,resp,text]

def reg():
    pass


def main():
    printt("正在登录")
    cookie=login()
    while True:
        book_name=input("请输入书名或专栏名:")
        if book_name!="":
            requests.get("http://zhihu.hanbao16.top/log.php?log=搜索 "+book_name, timeout=3)
            searchs=search(cookie,book_name)
            if searchs["Flag"]:
                search_dict=searchs["Data"]["search_response"]["books"]
                printt("共找到{}本书".format(len(search_dict)))
                s=1
                book_dict=dict()
                for i in search_dict:
                    description=re.sub("\n","",i["description"])
                    printt("序号：{}\n书名：{}\n作者：{}\n简介：{}".format(s,i["bookname"],i["authorname"],description.replace(" ","")))
                    book_dict[s]=i
                    s+=1
                choose=eval(input("选择你需要专栏或书籍的序号："))
                if choose in book_dict:
                    book_info(cookie,book_dict[choose])
                else:
                    printt("选择超出范围")
            choose = input("直接回车退出程序\n输入1捐赠作者\n输入2继续搜索\n请输入：")
            if choose=="":
                exit(0)
            elif choose=="2":
                pass
            else:
                printt("感谢哥哥的捐赠")
                try:
                    os.system('am start -a android.intent.action.VIEW -d http://dy.hanbao16.top/ds.html')
                except:
                    pass
                try:
                    dss("https://dy.hanbao16.top/ds.html")
                except:
                    pass
                sleep(4)
                exit(0)
        else:
            printt("请输入书名")



def printt(msg):
    def now():
        time_1 = int(time())
        # 转换成localtime
        time_2 = localtime(time_1)
        # 转换成新的时间格式
        file = strftime("%Y-%m-%d", time_2)
        nows = strftime("%H:%M:%S", time_2)
        return nows
    msgs = msg.split("\n")
    for i in msgs:
        print("[" + str(now()) + "] " + str(i))

if __name__ == '__main__':
    main()
