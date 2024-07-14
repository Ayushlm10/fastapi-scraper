import httpx
from bs4 import BeautifulSoup

import api.models as models


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
                product_title=name,
                product_price=price,
                path_to_image=image_link,
            )
        )
    return extracted_products
