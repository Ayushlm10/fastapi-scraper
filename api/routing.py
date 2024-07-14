import asyncio

import httpx
from fastapi import APIRouter

import scraper
from api import models

router = APIRouter(
    prefix="/scrape",
)


URL = "https://dentalstall.com/shop/page/"


def generate_urls(page_limit: int) -> list[str]:
    return [f"{URL}{page}" for page in range(1, page_limit + 1)]


@router.get("/")
async def scrape(page_limit: int = 5):
    urls = generate_urls(page_limit)

    async with httpx.AsyncClient() as client:
        products: models.ScrapedProducts = [scraper.scrape_page(client, url) for url in urls]
        scraped_results = await asyncio.gather(*products)
    return scraped_results
