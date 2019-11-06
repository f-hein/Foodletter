import logging

subs_filepath = 'subscribers_list.txt'


class MailingList:
    @staticmethod
    def add(email: str) -> None:
        with open(subs_filepath, 'a+') as subs_file:
            subs_file.seek(0)
            file_content = subs_file.read()
            if email not in file_content:
                subs_file.write(email+'\n')
                logging.info(f"Mail added to subscribers list: {email}")
            else:
                logging.error(f"Mail already added to subscribers list: {email}")

    @staticmethod
    def delete(email: str) -> None:
        with open(subs_filepath, 'r+') as subs_file:
            lines = subs_file.readlines()
            subs_file.seek(0)
            for line in lines:
                if email not in line:
                    subs_file.write(line)
                else:
                    logging.info(f"Mail deleted from subscribers list: {email}")
            subs_file.truncate()

    @staticmethod
    def get_mails() -> list:
        with open(subs_filepath, 'r') as subs_file:
            list_of_email_addresses = list(map(lambda x: x.rstrip(), subs_file.readlines()))
        return list_of_email_addresses
