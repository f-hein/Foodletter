import imaplib
import logging
import re
import smtplib
from datetime import date, datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from bot_credentials import gmail_user, gmail_password
from scraper import check_if_all_menus_exist, get_all_menus

logging.basicConfig(filename='mail_sender.log', filemode='w', format='%(asctime)s %(message)s', level=logging.INFO)
subscribers_list_fp = 'subscribers_list.txt'


class MailSender:
    def __init__(self):
        pass

    @staticmethod
    def _create_email(recipent: str, message: str) -> MIMEMultipart:
        msg = MIMEMultipart()
        msg['From'] = f"FoodBot <{gmail_user}>"
        msg['To'] = recipent
        msg['Subject'] = f"[FOODBOT][{date.today()}] What's cooking? :)"
        msg.attach(MIMEText(message, 'plain'))
        return msg

    @staticmethod
    def _get_email_body() -> str:
        template = "\n### {} ###\n{}"
        formatted_mesage = f'{date.today()}\n'
        for place_name, menu in get_all_menus().items():
            formatted_mesage += template.format(place_name.replace("_", " ").upper(), menu)
        return formatted_mesage

    def _send_email(self, recipient, message) -> None:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.send_message(self._create_email(recipient, message))
        logging.info(f"Mail sent to {recipient}")
        server.close()

    def send_email_to_many_recipients(self, recipients: list) -> None:
        msg_body = self._get_email_body()
        if check_if_all_menus_exist():
            for recipient in recipients:
                self._send_email(recipient, msg_body)
        else:
            print(f"[{datetime.now()}] Mails not sent. One of menus is not complete.")


class MailChecker:
    def __init__(self):
        self.imap = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        self.imap.login(gmail_user, gmail_password)
        self.imap.select('INBOX')

    def read_unseen_emails(self):
        _, response = self.imap.search(None, '(UNSEEN)')
        unread_mails_ids = response[0].split()
        for e_id in unread_mails_ids:
            _, body = self.imap.fetch(e_id, '(BODY[TEXT] BODY[HEADER.FIELDS (FROM)])')
            sender_email = re.findall('<(.*)>', str(body[1][1]))[0]
            if 'SUBSCRIBE' in body[1][1]:
                SubscriberList.add(sender_email)
            elif 'UNSUBSCRIBE' in body[1][1]:
                SubscriberList.delete(sender_email)


class SubscriberList:
    def __init__(self):
        pass

    @staticmethod
    def add(email):
        pass

    @staticmethod
    def delete(email):
        pass
