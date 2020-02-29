#inpired by https://stackoverflow.com/questions/24310945/group-items-by-string-pattern-in-python

try:
    from appdaemon.plugins.hass.hassapi import Hass
except:
    from hass import Hass

from datetime import datetime
from datetime import timedelta
from dateutil.parser import parse
import globals
from todoist.api import TodoistAPI
from plural import fmt

task_fmt1 = '{0:plural1|задача|задачи|задач}'
task_fmt2 = '{0:plural1|просроченная задача|просроченные задачи|просроченных задач}'
bill_fmt1 = '{0:plural1|платеж|платежа|платежей}'
bill_fmt2 = '{0:plural1|просроченный платеж|просроченных платежа|просроченных платежей}'
weekend_project_id = 2162787019
evening_project_id = 2228903924

class Todoist(Hass):
    def initialize(self):
        self.token = self.args['token']
        self.handle = self.run_hourly(self.get_tasks, globals.now())
        self.set_state("sensor.todoist_morning_message", state='?')

    def get_tasks(self, kwargs):
        today_count = due_count = bills_count = 'unknown'
        morning_msg = ""
        evening_msg = ""
        #try:
        api = TodoistAPI(self.token)
        api.sync()
        labels = {l['name']:l['id'] for l in api.state['labels']}
        tomorrow = datetime.utcnow() + timedelta(days=1)
        today = datetime.utcnow()
        allitems = list(filter(lambda x: x['due'] != None and x['date_completed'] is None,  api.state['items']))
        due = list(filter(lambda x: parse(x['due']['date']).replace(tzinfo=None).date() < today.date(), allitems))
        today = list(filter(lambda x: parse(x['due']['date']).replace(tzinfo=None).date() == today.date(), allitems))
        bills = list(filter(lambda x: labels['bills'] in x['labels'], today+due))
        weekend = list(filter(lambda x: x['project_id'] == weekend_project_id and x['date_completed'] is None, api.state['items']))
        evening = list(filter(lambda x: x['project_id'] == evening_project_id and x['date_completed'] is None, api.state['items']))

        evening_count = len(evening)
        today_count = len(today)
        due_count = len(due)
        bills_count = len(bills)
        bills_only = (due_count+today_count == bills_count)
        if bills_only:
            morning_msg = self.render_tasks(due_count, today_count, 0, bill_fmt1, bill_fmt2, bill_fmt1)
        else:
            morning_msg = self.render_tasks(due_count, today_count, bills_count, task_fmt1, task_fmt2, bill_fmt1)
        if not morning_msg:
            morning_msg = 'Все задачи выполнены!'
        morning_msg = f'Доброе утро. {morning_msg} Харошего дня'
        
        for task in evening:
            evening_msg += f"{task['content']}"

        if evening_msg:
            evening_msg = 'Напоминаю, вы хотели ' + evening_msg

        #except Exception as e:
        #    self.log(f'Some exception occurred {e}', level='ERROR')
        self.set_state("sensor.todoist_due_tasks", state = due_count)
        self.set_state("sensor.todoist_today_tasks", state = today_count)
        self.set_state("sensor.todoist_bill_tasks", state = bills_count)
        self.set_state("sensor.todoist_morning_message", state=morning_msg)
        self.set_state("sensor.todoist_evening_message", state=evening_msg)
        #self.set_state('sensor.todoist_test', state='test')
        self.log(f'{due_count=} {today_count=} {bills_count=} {evening_count=}')

    def render_tasks(self, due, today, bills, f1, f2, f3):
        msg = ""
        if today > 0:
            msg = fmt.format(f'В вашем списке на сегодня {f1}', today)
            if due > 0:
                msg += f', просрочено {due}'
        elif due > 0:
            msg = fmt.format(f'В вашем списке {f2}', due)
        if msg:
            if bills > 0:
                msg += fmt.format(f', из них {f3}.', bills)
        return msg

# it can be invoked from the command line without AppDaemon available 
if __name__ == '__main__':
    mock = TodoistDigest()
    mock.initialize()
    mock.get_tasks({})