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
import re

def parse(pageNo):
    data = []
    with open('./data/%d.json' % pageNo, 'r') as f:
        load_dict = json.load(f)
        data = load_dict['datas']
    return data

def filter_fund_rank(df):
    df_1 = df.sort_values(by='近1年', ascending=False).loc[0:2500/4]
    df_2 = df.sort_values(by='近2年', ascending=False).loc[0:2500/4]
    df_3 = df.sort_values(by='近3年', ascending=False).loc[0:2500/4]
    df_new = pd.merge(df_1, df_2, on='基金代码')
    df_new = pd.merge(df_new, df_3, on='基金代码')
    fund_ids = df_new['基金代码'].tolist()
    return fund_ids

def filter_fund_size(funds):
    match_funds = []
    for fund in funds:
        f_size = fund[1]
        p = re.compile(r'基金规模：(\d+(.\d+){0,1})亿元')
        m = p.match(f_size)
        if m:
            f_size = float(m.group(1))
            if f_size >= 20 and f_size <= 100:
                match_funds.append(fund)
    return match_funds

def filter_fund_managetime(funds):
    match_funds = []
    for fund in funds:
        f_managetime = fund[3]
        p = re.compile(r'(\d+)年')
        m = p.match(f_managetime)
        if m:
            f_managetime = int(m.group(1))
            if f_managetime >= 3:
                match_funds.append(fund)
    return match_funds

def fulter_fund_managenum(funds):
    match_funds = []
    for fund in funds:
        f_managenum = fund[4]
        p = re.compile(r'.*(\d+)只基金')
        m = p.match(f_managenum)
        if m:
            f_managenum = int(m.group(1))
            if f_managenum <= 3:
                match_funds.append(fund)
    return match_funds

def main():
    data = []
    for i in range(31):
        d = parse(i+1)
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
    #fund_ids = filter_fund_rank(df)
    funds = []
    with open('./data/fund_detail.json', 'r') as f:
        funds = json.load(f)
    funds = filter_fund_size(funds)
    funds = filter_fund_managetime(funds)
    funds = fulter_fund_managenum(funds)
    print(funds)
    df_filter = pd.DataFrame(funds)
    df_filter.columns = ['基金代码','规模','基金经理','从业时间','基金经理规模','经理星级']
    df = pd.merge(df, df_filter, on='基金代码')
    choose_columns = ['基金代码','基金名称','规模','近1年' , '近2年', '近3年', '今年来', '成立来','从业时间','基金经理规模']
    print(df.loc[:, choose_columns])
    
    
    
if __name__ == '__main__':
    main()