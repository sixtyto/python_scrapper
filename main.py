from sys import argv
from database import Database
from scrapper import Scrapper

arg = int(argv[1].replace("--0", "").replace("--", ""))

db = Database()
scrapper = Scrapper(db, arg)

scrapper.run()
