import re


def remove_spaces(text: str) -> str:
    return re.sub(' +', ' ', text).strip()


def col_or_row(content) -> str:
    if len(content.find_all('li', class_='product-item--row')) > 0:
        return content.find_all('li', class_='product-item--row')
    elif len(content.find_all('li', class_='product-item--column')) > 0:
        return content.find_all('li', class_='product-item--column')
    else:
        return ""


def get_link(content) -> str:
    return content.find('a', class_='product-title')['href']


def get_name(content) -> str:
    return remove_spaces(content.find('a', class_='product-title').get_text().replace("\n", ""))


def get_price(content) -> float:
    string = content.find('span', class_="promo-price")
    if string:
        string = string.get_text().strip()
    else:
        return 0
    string = string.replace("\n  ", ".")
    if string.split(".")[1] == "-":
        return float(string.split(".")[0] + '.00')
    else:
        return float(string)


def get_rating(content) -> float:
    rating = content.find("div", attrs={'data-test': 'rating-stars'})
    if rating:
        rating = remove_spaces(rating['title'])
        try:
            rating = float(rating)
        except:
            rating = 0.0
        return rating
    else:
        return 0.0


def get_brand(offer) -> str:
    brand = offer.find(attrs={'data-role': 'BRAND'})
    if not brand:
        return "n/a"
    else:
        return remove_spaces(brand.get_text())


def get_seller(offer) -> str:
    seller = offer.find('a', class_='product-seller__name')
    if not seller:
        return "Bol.com"
    else:
        return remove_spaces(seller.get_text().replace("\n", ""))


def get_image(offer) -> str:
    if offer.find('img', class_='js_product_img'):
        return offer.find('img', class_='js_product_img')['src']
    else:
        if offer.find('img', class_='js_product_thumb'):
            return offer.find('img', class_='js_product_thumb')['src']
        else:
            return 'no image'


def get_subcategory(offer):
    if offer.find("ul", class_='breadcrumbs'):
        return offer.find("ul", class_='breadcrumbs').findAll('li')[-1].get_text().replace("\n", "").strip()
    else:
        return None


def get_category(offer):
    if offer.find("ul", class_='breadcrumbs'):
        return offer.find("ul", class_='breadcrumbs').findAll('li')[1].get_text().replace("\n", "").strip()
    else:
        return None


def get_specification(offer):
    ean = 0
    weight = 'n/a'
    dimensions = 'n/a'
    specifications = offer.find(attrs={'data-test': 'specifications'})
    if specifications:
        specifications_titles = specifications.find_all('dt', class_="specs__title")
        specifications_values = specifications.find_all('dd', class_="specs__value")
        for index, item in enumerate(specifications_titles):
            specification_value = specifications_values[index].get_text().replace("\n", "").strip()
            if 'EAN' in item.get_text():
                ean = int(remove_spaces(specification_value.replace(" ", "")))
            if 'ewicht' in item.get_text():
                weight = specification_value
            if 'fmetingen' in item.get_text():
                dimensions = specification_value
        if dimensions == "n/a":
            for index, item in enumerate(specifications_titles):
                specification_value = specifications_values[index].get_text().replace("\n", "").strip()
                if specification_value == "Ja" or specification_value == "Nee":
                    continue
                else:
                    if 'reedte' in item.get_text():
                        if dimensions == "n/a":
                            dimensions = specification_value
                        else:
                            dimensions += ' x ' + specification_value
                    if 'oogte' in item.get_text():
                        if dimensions == "n/a":
                            dimensions = specification_value
                        else:
                            dimensions += ' x ' + specification_value
                    if 'engte' in item.get_text():
                        if dimensions == "n/a":
                            dimensions = specification_value
                        else:
                            dimensions += ' x ' + specification_value
    return ean, remove_spaces(dimensions), remove_spaces(weight)
