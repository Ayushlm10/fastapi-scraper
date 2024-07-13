import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Product(BaseModel):
    name: str
    price: str
    image_link: str


class ScrapedProducts(BaseModel):
    products: list[Product]


@app.get("/")
async def root():
    URL = "https://dentalstall.com/shop/page/1"
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    products = soup.findAll("li", class_=["product", "type-product"])
    extracted_products: ScrapedProducts = []
    for product in products:
        name_element = product.select_one(".product-inner .mf-product-details .mf-product-content h2 a")
        name = name_element.text.strip() if name_element else None
        price_element = product.select_one(
            ".product-inner .mf-product-details .mf-product-price-box .price ins .amount bdi"
        )
        if not price_element:
            price_element = product.select_one(
                ".product-inner .mf-product-details .mf-product-price-box .price .amount bdi"
            )
        price = price_element.text.strip() if price_element else None
        img_element = product.select_one(".product-inner .mf-product-thumbnail a img")
        image_link = img_element["data-lazy-src"] if img_element and "src" in img_element.attrs else None

        extracted_products.append(
            Product(
                name=name,
                price=price,
                image_link=image_link,
            )
        )
    return extracted_products
