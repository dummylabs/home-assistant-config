#encoding utf-8
import hashlib
import shelve
import sys
import re
from requests import ConnectionError
from bs4 import BeautifulSoup
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

try:
    from appdaemon.plugins.hass.hassapi import Hass
except:
    from hass import Hass


class WaterOutage(Hass):
    def initialize(self):
        self.handle = self.run_in(self.my_callback, 5)
        self.errors = self.get_app('errors')
        self.handle = self.run_hourly(self.my_callback, None)
        self.url = self.args['url']
        self.gmail_login = self.args['gmail_login']
        self.gmail_password = self.args['gmail_password']
        self.gmail_to = self.args['gmail_to'].split(',')

    def my_callback(self, kwargs):
        self.check_page(self.url)

    def get_hash(self, s):
        return hashlib.md5(s.encode()).hexdigest()

    def get_last_row(self, data):
        row = data.select('td#main-column')[0].table.select('tr')[1].select("td")
        for col in range(0, len(row)):
            if row[col].text.strip():
                yield row[col].text.strip()

    def send_mail(self, subj, text):
        subject = subj  
        body = text
        message = MIMEText(body, _charset="UTF-8")
        message['Subject'] = Header(subject, "utf-8")
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(self.gmail_login, self.gmail_password)
        server.sendmail(self.gmail_login, self.gmail_to, message.as_string())
        server.close()

        self.log(u'Email has been sent')

    def check_page(self, url):
        p = re.compile(u'(котельн.*6)|(ленинградск)',re.IGNORECASE)
        #p = re.compile(u'(Маяк)',re.IGNORECASE)
        try:
            raw_html = requests.get(url).text
            data = BeautifulSoup(raw_html, 'html.parser')
            last_row = self.get_last_row(data)
         
            date = last_row.__next__()
            date = re.sub('\s+',' ', date)
            kind =  last_row.__next__() 
            kind = re.sub('\s+',' ', kind)
            address = last_row.__next__() 
            address = re.sub('\n +\n','\n', address)
            address = re.sub(' +',' ', address)
            reason = last_row.__next__()
            reason = re.sub(' +',' ', reason)
            if not (date and kind and address):
                raise Exception('Failed to parse {} page, some mandatory fields are missing'.format(url))

            h = self.get_hash(date+kind+address+reason)

            with shelve.open('/config/appdaemon/apps/water_outage.db', 'c') as shelf:
                # shelf modified date can be used to check if script is alive
                shelf['alive'] = 0 if not 'alive' in shelf else shelf['alive'] + 1
                if h in shelf:
                    self.log(u'Page is up to date')
                else:        
                    if p.search(address):
                        self.log(u'Update found, sending notification')
                        msg = u"{} будет отключено {} \n************\n Причина: {}\n************\n{}".format(date, kind, reason, address)
                        self.send_mail(u"Внимание! Будет отключено {}".format(kind), msg)
                    shelf[h] = 1
            self.errors.reset()
        except ConnectionError as e:
            self.errors.add()
            self.log(u'{}'.format(e), level="ERROR")
        except Exception as e:
            self.errors.add()
            self.log(e, level="ERROR")

# it can be invoked from the command line without AppDaemon available 
if __name__ == '__main__':
    mock = WaterDog()
    mock.initialize()
    mock.my_callback({})