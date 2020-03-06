# Foodletter
Foodletter is a simple mailing app providing you with the newest foodcourts' menus located near TC Nokia Wroclaw - Green Towers A & B (Strzegomska 36) and West Link & West Gate (Szybowcowa 2). 
It uses gmail account to send scraped information about menus and receive subscription emails.

### What foodcourts exactly it scrapes?
***WL/WG location:***
- Cockpeat Wroclaw,
- Astra Catering,
- Obiadeo.

***GTA/GTB:***
- Kame Wroclaw,
- Green Towers Bistro

### How to use it?
Just download this repository - every scraper works OOTB.

Mailer won't work until provided with email and password in `bot_credentials.py` located in project's root directory. It needs to be created first!

Used variables' names are: `WL_USERNAME, WL_PASSWORD, WG_USERNAME, WG_PASSWORD`.
### private TODO list:
- [ ] Add unit tests
- [ ] Send mail to a newly subscribed person IF foodletter was sent that day
- [ ] Add Meet&Eat Wroclaw to GTA/GTB 
- [ ] Add backup of subscribers lists to cloud
