# -*- coding: utf-8 -*-
import logging
import os

from apscheduler.schedulers.blocking import BlockingScheduler

from logic.foodletter_logic import run_foodletter, create_state_files

logs_filepath = 'mail_logs.log'
logging.basicConfig(filename=logs_filepath, filemode='w', format='%(asctime)s %(message)s', level=logging.INFO)

if __name__ == '__main__':
    create_state_files()
    scheduler = BlockingScheduler()
    scheduler.add_job(run_foodletter, 'interval', minutes=1)
    print('Press Ctrl+{} to exit'.format('Break' if os.name == 'nt' else 'C'))
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
