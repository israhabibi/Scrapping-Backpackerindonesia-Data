from bs4 import BeautifulSoup
import requests
import json
import os
import sqlite3
import re
import datetime

connection = sqlite3.connect('bpiData.sqlite')

print ('Start...')

base_url =   'http://www.backpackerindonesia.com/trip'
start_page = 'http://www.backpackerindonesia.com'

def pars(url) :
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    next_page = start_page + soup.select('li.pager-next')[0].find('a').get("href")
    page = soup.select('li.pager-current')[0].get_text()
    print (page)
    print (next_page)
    rx = requests.get(next_page)
    soupx = BeautifulSoup(rx.content, 'html.parser')
    tbody = soupx.select('tbody')
    trs = soupx.select('tbody > tr')
    items = []
    for tr in trs:        
        td1 = tr.select('td.views-field-title')[0]
        td1a = td1.find('a')
        tglx = tr.select('td.views-field-field-tanggal-value')[0].get_text()
        tgl = tglx.strip()
        tglFrom = datetime.date.isoformat(datetime.datetime.strptime(str(datetime.date.today().year) +' '+ tgl.split(' - ')[0], "%Y %d %b").date())
        if len(tgl.split(' - ')) == 1:
            tglTox = datetime.date.isoformat(datetime.datetime.strptime(str(datetime.date.today().year) +' '+ tgl.split(' - ')[0], "%Y %d %b").date())
        else:
            tglTox = datetime.date.isoformat(datetime.datetime.strptime(str(datetime.date.today().year) +' '+ tgl.split(' - ')[1], "%Y %d %b").date())
        if tglTox < tglFrom :
            tglTo = datetime.date.isoformat(datetime.datetime.strptime(str(datetime.date.today().year+1) +' '+ tgl.split(' - ')[1], "%Y %d %b").date())
        else:
            tglTo = tglTox
        url = start_page + td1a.get("href")
        title = td1a.get_text()
        if td1.find('br').next_sibling.next_sibling.text == 'verified':
            authory = td1.find('br').next_sibling+td1.find('br').next_sibling.next_sibling.text+td1.find('br').next_sibling.next_sibling.next_sibling
        else :
            authory = td1.find('br').next_sibling
        authorx = authory.split('by ')[1].strip()
        author = authorx.strip().split(' on ')[0].strip()
        if td1.find('br').next_sibling.next_sibling.text == 'verified':
            tagy = td1.find('br').next_sibling.next_sibling.next_sibling.next_sibling.text.strip()
            # +td1.find('br').next_sibling.next_sibling.text+td1.find('br').next_sibling.next_sibling.next_sibling
        else :
            tagy = td1.find('br').next_sibling.next_sibling.text.strip()
        postDate = authorx.strip().split(' on ')[1]
        durasi = (datetime.datetime.strptime(tglTo, '%Y-%m-%d')-datetime.datetime.strptime(tglFrom, '%Y-%m-%d')).days + 1
        # print(tagy)
        cursor = connection.cursor()
        cursor.execute("INSERT INTO bpiData (url, title, author, postDate, tgl, tglFrom, tglTo, durasi, tag ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (url, title, author,postDate, tgl, tglFrom, tglTo, durasi, tagy))
        # cursor.execute("INSERT INTO bpiData (url, title, author, postDate, tgl, tglFrom, tglTo ) VALUES (?, ?, ?, ?, ?, ?, ?)", (url, title, author,postDate, tgl, tglFrom, tglTo))
        connection.commit()
    if int(page) < 15:
        pars(next_page)

pars(base_url)
connection.close()
print ('Done')

