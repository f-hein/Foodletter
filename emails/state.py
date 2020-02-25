from datetime import date, datetime, timedelta
from pathlib import Path


class State:
    def __init__(self, location="WL"):
        self.state_filepath = f'logger_state_{location}.txt'

    def mails_were_sent_today(self):
        with open(self.state_filepath, 'r') as state_file:
            last_sent_date = datetime.strptime(state_file.readlines()[1], "%Y-%m-%d").date()
        return last_sent_date == date.today()

    def create_state_file(self):
        state_file = Path(self.state_filepath)
        if not state_file.exists():
            with open(self.state_filepath, 'w') as state_file:
                state_file.write(f"Last sent:\n{date.today() - timedelta(1)}")

    def log_emails_were_sent(self):
        with open(self.state_filepath, 'w') as state_file:
            state_file.write(f"Last sent:\n{date.today()}")
