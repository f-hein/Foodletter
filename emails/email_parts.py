from datetime import date

footer = "\n\nhttps://pajacyk.pl/ - Kliknij i pomóż dzieciom!\n"\
                 "\n----------\n" \
                 "Autor: Filip Hein <filip.hein@nokia.com>\n" \
                 "ABY ODSUBSKRYBOWAĆ LISTĘ MAILINGOWĄ WYŚLIJ MAIL O TREŚCI 'UNSUBSCRIBE' NA ADRES BOTA."


def default_subject():
    return f"[FOODBOT][{date.today()}] What's cooking? :)"
