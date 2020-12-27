from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from dotenv import load_dotenv
from os import getenv

load_dotenv()
Base = declarative_base()


class Brands(Base):
    __tablename__ = 'brands'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(191), unique=True)

    products = relationship('Products', back_populates='brands')


class Categories(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(191), unique=True)

    products = relationship('Products', back_populates='categories')


class Subcategories(Base):
    __tablename__ = 'subcategories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(191), unique=True)

    products = relationship('Products', back_populates='subcategories')


class Products(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(191), nullable=False)
    ean = Column(Integer)
    product_img = Column(String(191), nullable=False)
    brand_id = Column(Integer, ForeignKey('brands.id'), nullable=False)
    dimensions = Column(String(191))
    weight = Column(String(191))
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    subcategory_id = Column(Integer, ForeignKey('subcategories.id'), nullable=False)

    brands = relationship('Brands', back_populates='products')
    categories = relationship('Categories', back_populates='products')
    subcategories = relationship('Subcategories', back_populates='products')
    followed_products = relationship('FollowedProducts', back_populates='products')
    offers = relationship('Offers', back_populates='products')


class Users(Base):
    __tablename__ = 'users'

    uid = Column(String(191), nullable=False, primary_key=True)

    followed_products = relationship('FollowedProducts', back_populates='users')


class FollowedProducts(Base):
    __tablename__ = 'followed_products'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(191), ForeignKey('users.uid'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)

    users = relationship('Users', back_populates='followed_products')
    products = relationship('Products', back_populates='followed_products')


class Portals(Base):
    __tablename__ = 'portals'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(191), unique=True)

    offers = relationship('Offers', back_populates='portals')


class Sellers(Base):
    __tablename__ = 'sellers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(191), unique=True)

    offers = relationship('Offers', back_populates='sellers')


class Offers(Base):
    __tablename__ = 'offers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    offer_url = Column(String(191), nullable=False)
    seller_id = Column(Integer, ForeignKey('sellers.id'), nullable=False)
    portal_id = Column(Integer, ForeignKey('portals.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)

    sellers = relationship('Sellers', back_populates='offers')
    portals = relationship('Portals', back_populates='offers')
    products = relationship('Products', back_populates='offers')
    price_history = relationship('PriceHistory', back_populates='offers')
    sales = relationship('Sales', back_populates='offers')


class PriceHistory(Base):
    __tablename__ = 'price_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    price = Column(Float, nullable=False)
    rating = Column(Float, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    offer_id = Column(Integer, ForeignKey('offers.id'), nullable=False)

    offers = relationship('Offers', back_populates='price_history')


class Sales(Base):
    __tablename__ = 'sales'

    id = Column(Integer, primary_key=True, autoincrement=True)
    offer_id = Column(Integer, ForeignKey('offers.id'), nullable=False)
    amount = Column(Integer, nullable=False)
    updated_at = Column(DateTime)

    offers = relationship('Offers', back_populates='sales')


class ProductsInSubcategory(Base):
    __tablename__ = 'products_in_subcategory'

    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(191), nullable=False)
    subcategory = Column(String(191), nullable=False)
    rows = Column(Integer, nullable=False)


class UpdatedAt(Base):
    __tablename__ = 'updated_at'

    updated_at = Column(DateTime, primary_key=True)


class ProductsCount(Base):
    __tablename__ = 'products_count'

    rows = Column(Integer, primary_key=True)


class CategoriesProductsCount(Base):
    __tablename__ = 'categories_products_count'

    rows = Column(Integer, primary_key=True)


class Database:
    def __init__(self, host=getenv('HOST'), port=getenv('PORT'), user=getenv('DB_USER'), password=getenv('DB_PASSWORD'),
                 database=getenv('DATABASE'), test=False):
        if test:
            self.engine = create_engine('sqlite:///database.db')
            self.create_database()
        else:
            self.engine = create_engine(f'mysql:///{user}:{password}@{host}:{port}/{database}')
        self.Session = sessionmaker(bind=self.engine)
        self.sess = self.Session()

    def create_database(self):
        Base.metadata.create_all(self.engine)

    def get_offer_id(self, offer_url: str) -> int:
        if offer_id := self.sess.query(Offers).filter_by(offer_url=offer_url).first():
            return offer_id.id
        return -1

    def get_brand_id(self, brand: str) -> int:
        if brand_id := self.sess.query(Brands).filter_by(name=brand).first():
            return brand_id.id
        else:
            self.sess.add(Brands(name=brand))
            self.sess.commit()
        return self.sess.query(Brands).filter_by(name=brand).first().id

    def get_category_id(self, category: str) -> int:
        if category_id := self.sess.query(Categories).filter_by(name=category).first():
            return category_id.id
        else:
            self.sess.add(Categories(name=category))
            self.sess.commit()
        return self.sess.query(Categories).filter_by(name=category).first().id

    def get_subcategory_id(self, subcategory: str) -> int:
        if subcategory_id := self.sess.query(Subcategories).filter_by(name=subcategory).first():
            return subcategory_id.id
        else:
            self.sess.add(Subcategories(name=subcategory))
            self.sess.commit()
        return self.sess.query(Subcategories).filter_by(name=subcategory).first().id

    def get_product_id(self, ean: int) -> int:
        if product_id := self.sess.query(Products).filter_by(ean=ean).first():
            return product_id.id
        return -1

    def get_products_urls(self, product_id: int) -> list:
        return self.sess.query(Offers).filter_by(product_id=product_id).all()

    def get_portal_id(self, portal: str) -> int:
        if portal_id := self.sess.query(Portals).filter_by(name=portal).first():
            return portal_id.id
        else:
            self.sess.add(Portals(name=portal))
            self.sess.commit()
        return self.sess.query(Portals).filter_by(name=portal).first().id

    def get_seller_id(self, seller: str) -> int:
        if seller_id := self.sess.query(Sellers).filter_by(name=seller).first():
            return seller_id.id
        else:
            self.sess.add(Sellers(name=seller))
            self.sess.commit()
        return self.sess.query(Sellers).filter_by(name=seller).first().id

    def update_database(self, offer_id: int, price: float, rating: float, updated_at):
        print(f"updating {offer_id}: {price}, {rating}")
        self.sess.add(PriceHistory(price=price, rating=rating, offer_id=offer_id, updated_at=updated_at))
        self.sess.commit()

    def add_new_record(self, name: str, ean: int, offer_url: str, product_img: str, seller: str, brand: str,
                       dimensions: str, weight: str, category: str, subcategory: str, price: float, rating: float,
                       portal: str, updated_at):
        print(f"adding {ean}: {offer_url}")
        self.sess.add(Products(name=name, ean=ean, product_img=product_img, brand_id=self.get_brand_id(brand=brand),
                               dimensions=dimensions, weight=weight, category_id=self.get_category_id(category=category),
                               subcategory_id=self.get_subcategory_id(subcategory=subcategory)))
        self.sess.commit()
        self.sess.add(Offers(offer_url=offer_url, seller_id=self.get_seller_id(seller=seller),
                             portal_id=self.get_portal_id(portal=portal), product_id=self.get_product_id(ean=ean)))
        self.sess.commit()
        self.sess.add(PriceHistory(price=price, rating=rating, offer_id=self.get_offer_id(offer_url=offer_url),
                                   updated_at=updated_at))
        self.sess.commit()

    def get_cart_urls(self) -> list:
        ids = self.sess.query(FollowedProducts).distinct().all()
        urls = []
        for ID in ids:
            urls.append((ID, self.get_products_urls(ID)))
        results = []
        for item in urls:
            offer_id = item[0]
            for url in item[1]:
                results.append((offer_id, url))
        return results

    def add_cart_amount(self, offer_id: int, amount: int, timestamp):
        self.sess.add(Sales(offer_id=offer_id, amount=amount, updated_at=timestamp))
        self.sess.commit()
