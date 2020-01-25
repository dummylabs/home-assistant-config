#encoding utf-8
import re,sys
from requests import ConnectionError
from bs4 import BeautifulSoup
import soupsieve
import requests
import globals

try:
    from appdaemon.plugins.hass.hassapi import Hass
except:
    from hass import Hass

class YandexWeather(Hass):
    def initialize(self):
        self.location = self.args['location']
        self.handle = self.run_every(self.my_callback, globals.now(), 15*60)
        self.errors = self.get_app('errors')

    def my_callback(self, kwargs):
        self.scrape_weather(self.location)

    def cleanup(self, temp):
        return temp.replace('−','-').replace('+','')

    def scrape_weather(self, url):
        p = re.compile(u'(дождь)',re.IGNORECASE)
        try:
            raw_html = requests.get(url).text
            #with open("raw.html", "w", encoding='utf8') as text_file:
            #    text_file.write(raw_html)
            data = BeautifulSoup(raw_html, 'html.parser')
            actual_temp = self.cleanup(data.select('div.fact__temp')[0].select("span.temp__value")[0].text)
            apparent_temp = self.cleanup(data.select('div.fact__feels-like')[0].select("span.temp__value")[0].text)
            self.set_state("sensor.yandex_weather_temperature", state = actual_temp, attributes = {"friendly_name": "Yandex Temperature", "unit_of_measurement": '°C'})
            self.set_state("sensor.yandex_weather_apparent_temperature", state = apparent_temp, attributes = {"friendly_name": "Yandex Apparent emperature", "unit_of_measurement": '°C'})
            mchs_alert = data.select('html')[0].select(".default-alert")
            if len(mchs_alert) > 0:
                self.set_state("sensor.yandex_weather_mchs_alert", state = "{}".format(mchs_alert[0].text), attributes = {"friendly_name": "Yandex MCHS alert"})
            nowcast = data.select('p.maps-widget-fact__title')
            if len(nowcast) > 0:
                nowcast = nowcast[0].text
            else:
                nowcast = ''
            self.set_state("sensor.yandex_weather_nowcast_alert", state = "{}".format(nowcast), attributes = {"friendly_name": "Yandex Nowcast"})
            #self.log("done parsing yandex weather ({})".format(actual_temp))
            self.errors.reset()

        except ConnectionError:
            self.errors.add()
            self.error(u'Bad response from page {}'.format(url), level="ERROR")
        except Exception as e:
            self.errors.add()
            self.error('"{}", line:{}'.format(str(e), sys.exc_info()[-1].tb_lineno), level="ERROR")

# it can be invoked from the command line without AppDaemon available 
if __name__ == '__main__':
    weather = YandexWeather()
    weather.initialize()
    weather.my_callback({})
