from os import getenv
from datetime import datetime
from requests import get, Session
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from functions import *
import itertools

load_dotenv()


class Scrapper:
    def __init__(self, database, argv=0):
        self.timestamp = datetime.now()
        self.bol_url = getenv("URL_BOL")
        self.db = database
        self.proxies = {
            'http': '',
            'https': ''
        }
        if argv in range(1, 29):
            self.category = f"{getenv('CATEGORIES_URL').split(',')[argv - 1]}?showAll=true"
            self.proxies_list = getenv('PROXY_LIST').split(",")[(argv * 3) - 3:argv * 3]
            self.iterate_proxies = itertools.cycle(self.proxies_list)
            self.subcategories_list = self.get_subcategories(self.category)
        else:
            self.proxies_list = []
            self.change_proxies(getenv('PROXY_LIST').split(",")[80:])
            self.category = []
            self.cart_urls = self.db.get_cart_urls()
            self.iterate_proxies = itertools.cycle(self.proxies_list)

    def set_time(self):
        self.timestamp = datetime.now()

    def change_proxies(self, proxy_list: list):
        self.proxies_list = proxy_list
        self.iterate_proxies = itertools.cycle(proxy_list)

    def switch_proxies(self):
        proxy = next(self.iterate_proxies)
        self.proxies['http'] = f'http://{proxy}'
        self.proxies['https'] = f'http://{proxy}'

    def check_proxies(self, url_to_get: str):
        self.switch_proxies()
        working = False
        while not working:
            try:
                return get(url_to_get, proxies=self.proxies)
            except:
                log_error(error_message=f'proxy: {self.proxies}', timestamp=self.timestamp)
                self.switch_proxies()

    def get_last_page(self, url: str) -> int:
        try:
            return int(BeautifulSoup(self.check_proxies(url).content, features='lxml').find('ul', class_="pagination")
                       .find_all('a', class_='js_pagination_item')[-2].get_text())
        except:
            return 1

    def set_current_amount(self, product_id: int, url: str):
        self.set_time()
        link = f"{self.bol_url}{url}"
        offer_content = self.check_proxies(link)
        offer = BeautifulSoup(offer_content.content, "html.parser")
        add_to_cart_url = offer.find('a', class_='js_btn_buy')
        if add_to_cart_url:
            add_to_cart_url = add_to_cart_url['href']
        if add_to_cart_url:
            add_to_cart_url = f"{self.bol_url}{add_to_cart_url.replace('quantity=1', 'quantity=500')}"
        else:
            log_error(error_message=f'cart, dostawa: {link}, {add_to_cart_url}', timestamp=self.timestamp)
            self.db.add_cart_amount(product_id, 0, self.timestamp)
            return

        with Session() as session:
            try:
                session.get(add_to_cart_url, proxies=self.proxies)
                cart_content = session.get('https://www.bol.com/nl/order/basket.html', proxies=self.proxies)
            except:
                log_error(error_message=f'cart, max: {link}, {add_to_cart_url}', timestamp=self.timestamp)
                self.db.add_cart_amount(product_id, 555, self.timestamp)
                return
        cart = BeautifulSoup(cart_content.content, features='lxml')
        amount = cart.find('select', class_='tst_item_count_selection').find_all('option', {'selected': True})
        if amount:
            amount = amount[0].get_text()
        else:
            log_error(error_message=f'cart, inny: {link}, {add_to_cart_url}', timestamp=self.timestamp)
            return
        self.db.add_cart_amount(product_id, amount, self.timestamp)

    def get_subcategories(self, url: str) -> list:
        subcategories = []
        sub_subcategories = []
        third_sub = []
        categories_content = self.check_proxies(f'{url}')
        categories_list = BeautifulSoup(categories_content.content, features='lxml')
        categories = categories_list.find('div', class_='category-tree-control')
        hrefs = categories.find_all('a', href=True, class_='px_listpage_categoriesleft_click')
        for href in hrefs:
            subcategories.append(f'{self.bol_url}{href["href"]}?showAll=true')
        print('1st:', len(subcategories))
        for subcategory in subcategories:
            sub_subcategory_content = self.check_proxies(subcategory)
            sub_categories_list = BeautifulSoup(sub_subcategory_content.content, features='lxml')
            sub_categories = sub_categories_list.find('div', class_='category-tree-control')
            try:
                sub_hrefs = sub_categories.find_all('a', href=True, class_='px_listpage_categoriesleft_click')
            except:
                sub_subcategories.append(subcategory)
                continue
            for href in sub_hrefs:
                sub_subcategories.append(f'{self.bol_url}{href["href"]}?showAll=true')
        print('2nd:', len(sub_subcategories))
        for third in sub_subcategories:
            third_subcategory_content = self.check_proxies(third)
            third_categories_list = BeautifulSoup(third_subcategory_content.content, features='lxml')
            third_categories = third_categories_list.find('div', class_='category-tree-control')
            try:
                third_hrefs = third_categories.find_all('a', href=True, class_='px_listpage_categoriesleft_click')
            except:
                third_sub.append(third)
                continue
            for href in third_hrefs:
                sub_subcategories.append(f'{self.bol_url}{href["href"]}?showAll=true')
        print('3rd:', len(third_sub))
        return third_sub

    def run(self):
        for sub in self.subcategories_list:

            last_page = self.get_last_page(sub)
            for page in range(1, last_page + 1):

                if page == 1:
                    offers_content = self.check_proxies(f'{sub}&sort=release_date1')
                else:
                    offers_content = self.check_proxies(f'{sub.split("?")[0]}?page={page}&sort=release_date1')

                offers_list = BeautifulSoup(offers_content.content, features='lxml')
                offers_list = col_or_row(offers_list)
                if not offers_list:
                    continue

                for offer in offers_list:
                    self.set_time()
                    offer_url = get_link(offer)
                    name = get_name(offer)
                    if len(offer_url) > 191 or len(name) > 191:
                        continue

                    price = get_price(offer)
                    if not price:
                        continue
                    rating = get_rating(offer)

                    offer_id = self.db.get_offer_id(offer_url)

                    if offer_id != -1:
                        self.db.update_database(offer_id=offer_id, price=price,
                                                rating=rating, updated_at=self.timestamp)
                        continue

                    offer_content = self.check_proxies(f'{self.bol_url}{offer_url}')
                    offer = BeautifulSoup(offer_content.content, features='lxml')

                    ean, dimensions, weight = get_specification(offer)
                    for _ in range(3):
                        if ean == 0:
                            offer_content = self.check_proxies(f'{self.bol_url}{offer_url}')
                            offer = BeautifulSoup(offer_content.content, features='lxml')
                            ean, dimensions, weight = get_specification(offer)

                    category = get_category(offer)
                    brand = get_brand(offer)
                    seller = get_seller(offer)
                    product_img = get_image(offer)
                    subcategory = get_subcategory(offer)

                    if not subcategory or ean == 0:
                        log_error(error_message=f'ean: {offer_url}', timestamp=self.timestamp)
                        continue

                    try:
                        self.db.add_new_record(name=name, ean=ean, offer_url=offer_url, product_img=product_img,
                                               seller=seller, brand=brand, dimensions=dimensions, weight=weight,
                                               category=category, subcategory=subcategory, price=price, rating=rating,
                                               portal='bol', updated_at=self.timestamp)
                    except:
                        log_error(error_message=f'add: {name}, {ean}, {offer_url}, {product_img}, {seller}, {brand},'
                                                f'{dimensions}, {weight}, {category}, {subcategory}, {price},'
                                                f'{rating}', timestamp=self.timestamp)
                        continue
