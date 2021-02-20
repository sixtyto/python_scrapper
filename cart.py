from database import Database
from scrapper import Scrapper
from dotenv import load_dotenv
from os import getenv
load_dotenv()

db = Database()
sc = Scrapper(db)
sc.change_proxies(getenv('PROXY_LIST').split(",")[80:])

cart_urls = db.get_cart_urls()
for url in cart_urls:
    if len(url) > 1:
        sc.set_current_amount(url[0][0], url[1][0])
