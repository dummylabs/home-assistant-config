import appdaemon.plugins.hass.hassapi as hass
import datetime

sensor_id = 'sensor.test_run_once'

class TestApp(hass.Hass):
    def initialize(self):
        for t in range(96):
            self.run_at(self.test, datetime.time(int(t/4), t%4 * 15, 0))

    def test(self, kwargs):
        try:
            num = int(self.get_state(sensor_id))
            num += 1
        except:
            num = 0
        self.set_state(sensor_id, state=num, attributes = {"unit_of_measurement": '°C'})
        self.log(f'Test fired {num}')
            
