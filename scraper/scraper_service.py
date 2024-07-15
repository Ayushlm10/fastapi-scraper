import asyncio
import re

import httpx
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential

import api.models as models
from interfaces.database_interface import DatabaseInterface


class ScraperService:
    def __init__(self, db_service: DatabaseInterface):
        self.db = db_service

    async def scrape_and_save(self, urls: list[str]) -> bool:
        scraped_results: list[models.Product] = []
        async with httpx.AsyncClient() as client:
            products: list[models.Product] = [self.scrape_page(client, url) for url in urls]
            scraped_results = await asyncio.gather(*products)
        return await self.db.add_products(scraped_results)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def scrape_page(self, client: httpx.AsyncClient, url: str) -> list[models.Product]:
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
            if price_element:
                price_text = price_element.get_text().strip()
                price = float(re.sub(r"[^\d.]", "", price_text))
            else:
                price = None

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
