import httpx
from bs4 import BeautifulSoup

import models

URL = "https://dentalstall.com/shop/page/"


def generate_urls(page_limit: int) -> list[str]:
    return [f"{URL}{page}" for page in range(1, page_limit + 1)]


async def scrape_page(client: httpx.AsyncClient, url: str) -> models.ScrapedProducts:
    print(f"scraping: {url}")
    products = await client.get(url, follow_redirects=True)
    products.raise_for_status()
    soup = BeautifulSoup(products.content, "html.parser")
    products = soup.findAll("li", class_=["product", "type-product"])
    extracted_products: models.ScrapedProducts = []
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
            models.Product(
                name=name,
                price=price,
                image_link=image_link,
            )
        )
    return extracted_products
