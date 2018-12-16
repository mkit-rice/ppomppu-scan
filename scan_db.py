#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
import sys
import config
import datetime
import smtplib
import sqlite3
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bs4 import BeautifulSoup as bs
from urllib import parse

# db connect
conn = sqlite3.connect('search.db')
curs = conn.cursor()

# Create table
curs.execute('''CREATE TABLE IF NOT EXISTS history
            (keyword TEXT, no INTEGER)''')
conn.commit()


SMTP_INFO = config.SMTP_INFO
today = datetime.datetime.now().strftime("%Y.%m.%d")[2:10] #18-10-31

with requests.Session() as s:
  keyword = sys.argv[1]
  keywordQuery = parse.urlencode(parse.parse_qs('keyword='+keyword), doseq=True)

  no = []
  msg = ''
  lastNo = 0

  first_page = s.get('http://www.ppomppu.co.kr/zboard/zboard.php?id=ppomppu&search_type=sub_memo&'+str(keywordQuery))
  html = first_page.text
  soup = bs(html, 'html.parser')
  items = soup.select(
    '.list0'
  )

  for item in items:
    a = item.find('table').findAll('a')[1]
    title = a.get_text()
    link = a.get('href')
    nowNo = link.split('no=')[1].split('&')[0]

    # db 조회
    search = (keyword,nowNo,)
    curs.execute('SELECT * FROM history WHERE keyword=? AND no=?',search)
    if curs.fetchone():
      sys.exit()
    else:
      msg = msg + '<a href="http://www.ppomppu.co.kr/zboard/view.php?id=ppomppu&no='+nowNo+'" target="_blank">'+title+'</a><br/>'
      no.append(nowNo)


  # 첫글 번호 저장
  if len(no) > 0:
    values = [(keyword,no[0])]
    curs.executemany('insert into history values(?,?)', values)
    conn.commit()
    # print('insert db',values)

    # 메일 발송
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

