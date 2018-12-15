#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
import sys
import config
import datetime

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bs4 import BeautifulSoup as bs

SMTP_INFO = config.SMTP_INFO
today = datetime.datetime.now().strftime("%Y-%m-%d")[2:10] #18-10-31

with requests.Session() as s:
  keyword = sys.argv[1]
  no = []
  msg = ''
  lastNo = 0

  first_page = s.get('http://www.ppomppu.co.kr/zboard/zboard.php?id=ppomppu&search_type=sub_memo&keyword='+str(keyword))
  html = first_page.text
  soup = bs(html, 'html.parser')
  items = soup.select(
    '.list0 table a'
  )

  # 첫글 번호 읽기
  f = open("/Users/i2801/python/ppomppu/last.txt", 'r')
  while True:
      line = f.readline()
      if not line: break
      lastNo = int(line)
  f.close()

  for item in items:
    title = item.get_text()
    link = item.get('href')
    nowNo = link.split('no=')[1].split('&')[0]

    if int(nowNo) == int(lastNo):
      continue

    if int(nowNo) > int(lastNo):
      msg = msg + '<a href="http://www.ppomppu.co.kr/zboard/view.php?id=ppomppu&no='+nowNo+'" target="_blank">'+title+'</a><br/>'
      no.append(nowNo)

  # 첫글 번호 저장
  if len(no) > 0:
    f = open("/Users/i2801/python/ppomppu/last.txt", 'w')
    f.write(no[0])
    f.close()

    if msg != '':
      email = config.SMTP_INFO["email"]
      passwd = config.SMTP_INFO["passwd"]
      toEmail = config.SMTP_INFO["toEmail"]
      smtp = smtplib.SMTP('smtp.gmail.com', 587)
      smtp.ehlo()
      smtp.starttls()
      smtp.login(email, passwd)
      mail_msg = MIMEMultipart('alternative')
      mail_msg['Subject'] = '['+today+'] 뽐뿌 ' + str(keyword)
      mail_msg['To'] = toEmail
      mail_msg.attach(MIMEText(msg, 'html'))
      smtp.sendmail(email, toEmail, mail_msg.as_string())
      smtp.quit()

