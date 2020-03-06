import imaplib
import re

from emails import MailingList, MailCreator, MailSender


class SubscriptionChecker:
    def __init__(self, email, password, site, send_confirmation_mails=True):
        self.email = email
        self.password = password
        self.site = site
        self.send_confirmation_mails = send_confirmation_mails
        self.imap = None

    def check(self) -> None:
        self._create_imap_connection_and_select_inbox()
        unread_mails_ids = self._get_unread_mails_ids()
        for email_id in unread_mails_ids:
            sender_email, subject, body = self._get_core_data_by_email_id(email_id)
            self._check_subscription_requests(sender_email, subject, body)
        self._delete_imap_connection()

    def _create_imap_connection_and_select_inbox(self):
        self.imap = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        self.imap.login(self.email, self.password)
        self.imap.select('INBOX')

    def _delete_imap_connection(self):
        self.imap.close()
        del self.imap

    @staticmethod
    def _get_sender_mail(body) -> str:
        return re.findall('<(.*)>', str(body[1][1]))[0]

    @staticmethod
    def _get_subject(body) -> str:
        subject = re.findall('(?<=Subject: )[a-zA-Z ]*', str(body[1][1]))
        return subject[0].upper() if subject else ''

    def _check_subscription_requests(self, sender_email: str, subject: str, body: str) -> None:
        key_words = ['UNSUBSCRIBE', 'SUBSCRIBE']
        for key_word in key_words:
            if key_word in subject or key_word in body:
                MailingList(self.site).add(sender_email) if key_word == 'SUBSCRIBE' \
                    else MailingList(self.site).delete(sender_email)
                if self.send_confirmation_mails:
                    self._send_confirmation_email(key_word, sender_email)

    def _send_confirmation_email(self, subscribe_state, recipient) -> None:
        subject = f"{subscribe_state.lower()}d".capitalize()
        body = f"You've been successfully {subscribe_state.lower()}d!"
        email_object = MailCreator().create_email(recipient, self.email, subject=subject, msg_body=body,
                                                  use_mail_template=False)
        MailSender(self.email, self.password).send_mail_to_one_recipient(recipient, email_object)

    def _get_unread_mails_ids(self):
        _, response = self.imap.search(None, '(UNSEEN)')
        return response[0].split()

    def _get_core_data_by_email_id(self, email_id) -> tuple:
        _, body = self.imap.fetch(email_id, '(BODY[TEXT] BODY[HEADER.FIELDS (FROM SUBJECT)])')
        sender_email = self._get_sender_mail(body)
        subject = self._get_subject(body)
        body = str(body[0][1]).upper()
        return sender_email, subject, body
