# -*- coding: utf-8 -*-
import logging
import os

from apscheduler.schedulers.blocking import BlockingScheduler

from logic import FoodletterLogic

logs_filepath = 'mail_logs.log'
logging.basicConfig(filename=logs_filepath, filemode='w', format='%(asctime)s %(message)s', level=logging.INFO)

if __name__ == '__main__':
    logic = FoodletterLogic()
    scheduler = BlockingScheduler()
    scheduler.add_job(logic.run_foodletter, 'interval', minutes=5)
    print('Press Ctrl+{} to exit'.format('Break' if os.name == 'nt' else 'C'))
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
