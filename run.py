#!/usr/bin/env python
# -- coding: utf-8 --
import re
import requests
import time
from bs4 import BeautifulSoup

req = requests.Session()
finish = False

info = {
            'id' : '##PSU PASSPORT##', #EXAMPLE '5xxxxxxxxx'
            'pwd' : '##PASSWORD##', #EXAMPLE '1234'
            'term' : '##TERM##', #EXAMPLE '2'
            'year' : '##YEAR##', #EXAMPLE '2559'
        }

subject = {
    'id' : '##SUBJECT ID##', #EXAMPLE '140-452'
    'sec' : '##SECTION##', #EXAMPLE '02'
    'credit' : '##CREDIT##', #EXAMPLE '3'
}

urls = {
            'host' : 'https://sis-phuket5.psu.ac.th/WebRegist2005/Enroll/',
            'login' : 'https://sis-phuket5.psu.ac.th/WebRegist2005/Login.aspx',
            'searchsubject' : 'https://sis-phuket5.psu.ac.th/WebRegist2005/Enroll/FindOpenSubject.aspx',
            'selectsemester' : 'https://sis-phuket5.psu.ac.th/WebRegist2005/Enroll/Default.aspx',
            'comfirm' : 'https://sis-phuket5.psu.ac.th/WebRegist2005/Enroll/EnrollDetail.aspx',
            'infomation' : 'https://sis-phuket5.psu.ac.th/WebRegist2005/Student/StudentSISInfo.aspx'
        }

headers = {}

def getcsrftoken(url):
    r = req.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    __VIEWSTATE = soup.find('input' , id='__VIEWSTATE')
    __VIEWSTATEGENERATOR = soup.find('input' , id='__VIEWSTATEGENERATOR')
    __VIEWSTATEENCRYPTED = soup.find('input' , id='__VIEWSTATEENCRYPTED')
    __PREVIOUSPAGE = soup.find('input' , id='__PREVIOUSPAGE')
    return True , __VIEWSTATE , __VIEWSTATEGENERATOR , __PREVIOUSPAGE , __VIEWSTATEENCRYPTED , r.content

def getcookielogin():
    if '.ASPXAUTH' not in req.cookies:
        return False
    else:
        headers['Cookie'] = '.ASPXAUTH'+req.cookies['.ASPXAUTH']+'; '
        return True

def login():
    isget , __VIEWSTATE , __VIEWSTATEGENERATOR , _ , _ , _ = getcsrftoken(urls['login'])
    if isget :
        payload = {
                    '__LASTFOCUS' : '',
                    '__EVENTTARGET' : 'ctl00$mainContent$Login1$LoginButton',
                    '__EVENTARGUMENT' : '',
                    '__VIEWSTATE' : __VIEWSTATE['value'],
                    '__VIEWSTATEGENERATOR' : __VIEWSTATEGENERATOR['value'],
                    'ctl00$mainContent$Login1$UserName' : info['id'],
                    'ctl00$mainContent$Login1$Password' : info['pwd']
                }
        r = req.post(urls['login'] , data = payload)
        if getcookielogin():
            if info['id'] in str(r.content):
                print('[+]Login Complete')
                return True
            else:
                print('[+]Login Fail')
                return False
    return False

def selectsemester():
    isget , __VIEWSTATE , __VIEWSTATEGENERATOR , __PREVIOUSPAGE , _ , _ = getcsrftoken(urls['selectsemester'])
    payload = {
                '__EVENTTARGET' : '',
                '__EVENTARGUMENT' : '',
                '__VIEWSTATE' : __VIEWSTATE['value'],
                '__VIEWSTATEGENERATOR' : __VIEWSTATEGENERATOR['value'],
                '__PREVIOUSPAGE' : __PREVIOUSPAGE['value'],
                'ctl00$ctl00$mainContent$PageContent$DropDownList1' : info['term']+'/'+info['year'],
                'ctl00$ctl00$mainContent$PageContent$nextButton' : 'Next>>'
            }
    r = req.post(urls['selectsemester'] , data = payload)
    if 'Add New Subject' in str(r.content):
        print('[+]Select Semester')
        return True
    else:
        return False

def findsubject(r):
    try:
        soup = BeautifulSoup(r.content, 'html.parser')
        submit = soup.find('input' , value='Select')['onclick']

        if submit is not None:
            part = submit.split(',')[4]
            part = part.replace(" ", "")
            part = part.replace("\"", "")
            return part
        else:
            return False
    except:
        return False

def searchsubject():
    isget , __VIEWSTATE , __VIEWSTATEGENERATOR , __PREVIOUSPAGE , _ , _ = getcsrftoken(urls['searchsubject'])
    if isget :
        payload = {
                    '__LASTFOCUS' : '',
                    '__EVENTTARGET' : '',
                    '__EVENTARGUMENT' : '',
                    '__VIEWSTATE' : __VIEWSTATE['value'],
                    '__VIEWSTATEGENERATOR' : __VIEWSTATEGENERATOR['value'],
                    '__PREVIOUSPAGE' : __PREVIOUSPAGE['value'],
                    'ctl00$ctl00$mainContent$PageContent$UcFindSubject1$txtKeyWord': subject['id'],
                    'ctl00$ctl00$mainContent$PageContent$UcFindSubject1$btnFindSubject': '   Search   ',
                    'ctl00$ctl00$mainContent$PageContent$UcFindSubject1$hdKeyword': '',
                    'ctl00$ctl00$mainContent$PageContent$UcFindSubject1$hdTerm': '0',
                    'ctl00$ctl00$mainContent$PageContent$UcFindSubject1$hdYear': '0'
                }
        r = req.post(urls['searchsubject'] , data = payload)
        part = findsubject(r)
        if part is not False:
            print("[+]Found Subject %s" % (subject['id']))
            return "%s%s" % (urls['host'],part)
        else:
            print("[-]Not Found Subject")
            return False

def check(url):
    isget , __VIEWSTATE , __VIEWSTATEGENERATOR , __PREVIOUSPAGE , _ , content = getcsrftoken(url)
    if isget :
        aSubjectID =  re.search("aSubjectID=(\d+)", url).group(1)
        aSubjectOfferID =  re.search("aSubjectOfferID=(\d+)", url).group(1)
        soup = BeautifulSoup(content, 'html.parser')
        table = soup.find('table' , id='ctl00_ctl00_mainContent_PageContent_UcSectionOfferDetail1_gvSectionDetail')
        Alltr = table.find_all('tr')
        for i, tr in enumerate(Alltr):
            if len(tr.find_all('td')) > 0:
                if tr.find_all('td')[0].text == subject['sec']:
                    if int(tr.find_all('td')[2].text) < int(tr.find_all('td')[3].text):
                        payload = {
                                    '__LASTFOCUS' : '',
                                    '__EVENTTARGET' : '',
                                    '__EVENTARGUMENT' : '',
                                    '__VIEWSTATE' : __VIEWSTATE['value'],
                                    '__VIEWSTATEGENERATOR' : __VIEWSTATEGENERATOR['value'],
                                    '__PREVIOUSPAGE' : __PREVIOUSPAGE['value'],
                                    'ctl00$ctl00$mainContent$PageContent$hdSubjectID' : aSubjectID,
                                    'ctl00$ctl00$mainContent$PageContent$hidCredit' : '',
                                    'ctl00$ctl00$mainContent$PageContent$hidSubjectType' : '',
                                    'ctl00$ctl00$mainContent$PageContent$gvPendingEnroll$ctl02$ddlSection' : "%s%s" % (aSubjectOfferID,subject['sec']),
                                    'ctl00$ctl00$mainContent$PageContent$gvPendingEnroll$ctl02$ddlRegistType' : 'C',
                                    'ctl00$ctl00$mainContent$PageContent$btnAdd' : 'Add for Registration',
                                    'ctl00$ctl00$mainContent$PageContent$UcSectionOfferDetail1$hidSubjectOfferID' : aSubjectOfferID
                                }
                        r = req.post(url , data = payload)
                        if 'Add New Subject' in str(r.content):
                            return comfirm()
                else:
                    if i == len(tr)-2:
                        print("[-]Not Found Section")
                        return "nfsec"
    return False
def comfirm():
    isget , __VIEWSTATE , __VIEWSTATEGENERATOR , __PREVIOUSPAGE , _ , content = getcsrftoken(urls['comfirm'])
    if 'awaited confirmed registration subject data, not found' in str(content):
        pass
    else:
        payload = {
                    '__EVENTTARGET' : '',
                    '__EVENTARGUMENT' : '',
                    '__VIEWSTATE' : __VIEWSTATE['value'],
                    '__VIEWSTATEGENERATOR' : __VIEWSTATEGENERATOR['value'],
                    '__VIEWSTATEENCRYPTED' : '',
                    '__PREVIOUSPAGE' : __PREVIOUSPAGE['value'],
                    'ctl00$ctl00$mainContent$PageContent$btnConfirm' : 'Confirm The Registration'
                }
        r = req.post(urls['comfirm'] , data = payload)
        if 'Confirm Registration succeeded' in str(r.content):
            print("[+]Confirm Registration succeeded")
            global finish
            finish = True
    return finish
if login():
    if selectsemester():
        url = searchsubject()
        if url is not False:
            while not finish:
                r = check(url)
                if r is True:
                    pass
                elif r is "nfsec":
                    break
                elif r is False:
                    print(time.strftime("[-]Unavailable %a, %d %b %Y %H:%M:%S", time.gmtime()))
                    time.sleep(10)
