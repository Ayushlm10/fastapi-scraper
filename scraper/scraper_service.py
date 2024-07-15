import asyncio
import re

import httpx
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential

import api.models as models
from interfaces.cache_interface import CacheInterface
from interfaces.database_interface import DatabaseInterface
from interfaces.notifications_interface import NotificationsInterface


class ScraperService:
    def __init__(
        self, db_service: DatabaseInterface, notifications: NotificationsInterface, cache: CacheInterface = None
    ):
        self.db = db_service
        self.notifications = notifications
        self.cache = cache
        self.scraped_count = 0
        self.event_loop = asyncio.get_event_loop()
        asyncio.set_event_loop(self.event_loop)

    async def scrape_and_save(self, urls: list[str], proxy: str = None) -> bool:
        scraped_results: list[models.Product] = []
        async with httpx.AsyncClient(proxies=proxy) as client:
            products: list[models.Product] = [self.scrape_page(client, url) for url in urls]
            scraped_results = await asyncio.gather(*products)

        # scraped_count = sum(len(product_list) for product_list in scraped_results)
        updated_count = await self.db.add_products(scraped_results)
        message = (
            f"[Notification service] Scraped {self.scraped_count} products and updated {updated_count} products in db."
        )
        self.notifications.send_notifications(message)
        return True

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

            product_model = models.Product(
                product_title=name,
                product_price=price,
                path_to_image=image_link,
            )
            self.scraped_count += 1
            if self.cache:
                cached_product = await self.cache.get(product_model.product_title)
                if cached_product:
                    cached_product = models.Product.model_validate_json(cached_product)
                    if cached_product.product_price == product_model.product_price:
                        continue
                await self.cache.set(product_model.product_title, product_model.model_dump_json())
            extracted_products.append(product_model)
        return extracted_products

    async def get_all_products(self) -> list[models.Product]:
        return await self.db.get_all_products()

    async def clear_products(self) -> bool:
        success = await self.db.clear_all_products()
        if success:
            if self.cache:
                await self.cache.clear_cache()
        return success
