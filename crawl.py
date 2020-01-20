#!/usr/bin/env python 
#-*- coding: UTF-8 -*-
###########################################################################
#
# Copyright (c) 2018 www.codingchen.com, Inc. All Rights Reserved
#
##########################################################################
'''
  @brief a spider of 天天基金(http://fund.eastmoney.com)
  @author chenhui
  @date 2018-12-17 19:12:24
'''
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import js2py
import json
import time
import random
import pandas as pd

def crawlbyPage(totalPage):
    """
    分页抓取基金数据
    """
    print('totalPage: %s' % totalPage)
    for pageNo in range(1, totalPage+1):
        url = 'https://fundapi.eastmoney.com/fundtradenew.aspx'
        url += '?ft=hh&sc=1n&st=desc&pi=%d&pn=100' % pageNo
        url += '&cp=&ct=&cd=&ms=&fr=&plevel=&fst=&ftype=&fr1=&fl=0&isab='
        print('start get url:  %s' % url)
        content = requests.get(url)
        data = js2py.eval_js(content.text)
        new_dict = json.loads(str(data).replace("'", '"'))
        with open('./data/%d.json' % pageNo, 'w') as f:
            json.dump(new_dict, f)
        time.sleep(random.randint(5,8))

def crawl_details(fund_ids):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    # Chrome driver download path: https://chromedriver.chromium.org/downloads
    driver = webdriver.Chrome('/Users/chenhui/Code/fund/chromedriver', chrome_options=chrome_options)
    fund_details = []
    for fund_id in fund_ids:
        # 基金代码
        fund = [fund_id]
        print("start crawl http://fund.eastmoney.com/%s.html" % fund_id)
        driver.get("http://fund.eastmoney.com/%s.html" % fund_id)
        time.sleep(random.randint(3,5))
        # 保存请求的html文件，方便回溯数据
        with open('./fund_detail/%s.html' % fund_id, 'w') as f:
            f.write(driver.page_source)
        # 通过xpath获取 基金规模、经理、经理年限、经理同时管理的基金数,经理星级
        xpaths = [
            '//div[@class="infoOfFund"]/table/tbody/tr[1]/td[2]',
            '//div[@class="ManagerInfo"]/div[@class="M_name"]/a',
            '//div[@class="ManagerInfo"]/div[@class="M_date"]',
            '//div[@class="ManagerInfo"]/div[@class="fundScale"]',
            '//div[@class="ManagerInfo"]/div[@class="infoTips M_levels"]'
        ]
        for x in xpaths:
            try:
                node = driver.find_element_by_xpath(x)
                fund.append(node.text)
            except Exception as e:
                print('%s has exception with xpath %s' % (fund_id, x))
                print(e)
                fund.append('ERR')

        fund_details.append(fund)
    # 聚合所有detail数据至一个json文件中
    with open('./data/fund_detail.json', 'w') as f:
        json.dump(fund_details, f)
    driver.close()

def get_total_page():
    """
    获取total page
    """
    with open('./data/1.json', 'r') as f:
        load_dict = json.load(f)
    if load_dict['allPages']:
        return load_dict['allPages']
    else:
        return -1

def parse(totalPage):
    data = []
    for pageNo in range(1, totalPage+1):
        d = []
        with open('./data/%d.json' % pageNo, 'r') as f:
            load_dict = json.load(f)
            d = load_dict['datas']
        data.extend(d)
    data = list(map(lambda x: x.split('|'), data))
    df = pd.DataFrame(data)
    df.columns = ['基金代码', '基金名称', '类型', '日期', '单位净值', '日增长率', 
              '近1周', '近1月', '近3月', '近6月', '近1年' , '近2年', '近3年', '今年来', '成立来',
             '16','17','18','19','20','21','22','23','24','起购金额','26','手续费','28','29']
    choose_columns = ['基金代码', '基金名称', '类型', '日期', '单位净值', '日增长率',
                  '近1周', '近1月', '近3月', '近6月', '近1年' , '近2年', '近3年', '今年来', '成立来', '起购金额', '日增长率']
    df = df.loc[:, choose_columns]
    df = df.replace('', '-200')
    df[['近1年','近2年','近3年']] = df[['近1年','近2年','近3年']].astype(float)
    return df

def filter_fund_rank(df):
    """
    按近3年都能排在top300的规则来粗筛基金，避免抓取过多的基金详情数据
    """
    df_1 = df.sort_values(by='近1年', ascending=False).reset_index().loc[0:300]
    df_2 = df.sort_values(by='近2年', ascending=False).reset_index().loc[0:300]
    df_3 = df.sort_values(by='近3年', ascending=False).reset_index().loc[0:300]
    df_new = pd.merge(df_1, df_2, on='基金代码')
    df_new = pd.merge(df_new, df_3, on='基金代码')
    fund_ids = df_new['基金代码'].tolist()
    return fund_ids

def main(): 
    crawlbyPage(1)
    total_page = get_total_page()
    crawlbyPage(total_page)
    df = parse(total_page)
    fund_ids = filter_fund_rank(df)
    print(fund_ids)
    print(len(fund_ids))
    crawl_details(fund_ids)

if __name__ == '__main__':
    main()