import smtplib
from datetime import date, datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from bot_credentials import gmail_user, gmail_password
from scraper import get_all_menus


def create_email(recipent: str, message: str) -> MIMEMultipart:
    msg = MIMEMultipart()
    msg['From'] = f"FoodBot <{gmail_user}>"
    msg['To'] = recipent
    msg['Subject'] = f"[FOODBOT][{date.today()}] What's cooking? :)"
    msg.attach(MIMEText(message, 'plain'))
    return msg


def get_email_body() -> str:
    template = "\n### {} ###\n{}"
    formatted_mesage = f'{date.today()}\n'
    for place_name, menu in get_all_menus().items():
        formatted_mesage += template.format(place_name.replace("_", " ").upper(), menu)
    return formatted_mesage


def send_email(recipient, message) -> None:
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login(gmail_user, gmail_password)
    server.send_message(create_email(recipient, message))
    print(f"{date.today()}")
    server.close()

def send_email_to_many_recipients(recipients: list, message: str) -> None:
    msg_body = get_email_body()
    if check_if_all_menus_exist():
        for recipient in recipients:
            send_email(recipient, msg_body)
    else:
        print(f"[{datetime.now()}] Mails not sent. One of menus is not complete.")

def check_if_all_menus_exist() -> bool:
    return '' not in get_all_menus().values()