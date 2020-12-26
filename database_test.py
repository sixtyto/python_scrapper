from database import *
from datetime import datetime

database = Database(test=True)

database.add_new_record(
        name='Testowy produkt',
        ean=8457251369584,
        offer_url='www.test.pl',
        product_img='smutna_zaba.jpg',
        seller='Chiński sprzedawca jaj',
        brand='Keep away from fire',
        dimensions='12 x 12 x 12',
        weight='12 kg',
        category='Produkty testowe',
        subcategory='Smutne żaby',
        price=123.12,
        rating=4.4,
        updated_at=datetime.now())


def test_get_category_id():
    assert database.get_category_id('Produkty testowe') == 1
    assert database.get_category_id('Testowanko') == 2
    assert database.get_category_id('Produkty testowe') == 1


def test_get_subcategory_id():
    assert database.get_subcategory_id('Smutne żaby') == 1
    assert database.get_subcategory_id('Smutne łosie') == 2
    assert database.get_subcategory_id('Smutne żaby') == 1


def test_get_offer_id():
    assert database.get_offer_id('www.test.pl') == 1
    assert database.get_offer_id('www.pl') == -1


def test_get_brand_id():
    assert database.get_brand_id('Keep away from fire') == 1
    assert database.get_brand_id('Lodówka') == 2
    assert database.get_brand_id('Keep away from fire') == 1


def test_get_product_id():
    assert database.get_product_id(8457251369584) == 1
    assert database.get_product_id(845721369584) == -1


def test_get_products_url():
    assert database.get_products_urls(1)[0].offer_url == 'www.test.pl'


def test_add_cart_amount():
    database.add_cart_amount(amount=10, offer_id=1, timestamp=datetime.now())
    database.add_cart_amount(amount=14, offer_id=2, timestamp=datetime.now())
    database.add_cart_amount(amount=12, offer_id=3, timestamp=datetime.now())
    assert database.sess.query(Sales).filter_by(offer_id=1).first().amount == 10
    assert database.sess.query(Sales).filter_by(offer_id=2).first().amount == 14
    assert database.sess.query(Sales).filter_by(offer_id=3).first().amount == 12
