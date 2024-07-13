import asyncio

import httpx
from fastapi import FastAPI

import models
import scraper

app = FastAPI()


@app.get("/")
async def root(page_limit: int = 5):
    urls = scraper.generate_urls(page_limit)

    async with httpx.AsyncClient() as client:
        products: models.ScrapedProducts = [scraper.scrape_page(client, url) for url in urls]
        scraped_results = await asyncio.gather(*products)
    return scraped_results
