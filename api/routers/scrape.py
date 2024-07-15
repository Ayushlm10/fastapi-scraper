from fastapi import APIRouter, Depends

from api.services.json_db_service import JSONDatabaseService
from interfaces.database_interface import DatabaseInterface
from scraper.scraper_service import ScraperService as Scraper

router = APIRouter(
    prefix="/scrape",
)


def get_db_client() -> DatabaseInterface:
    return JSONDatabaseService("products.json")


def get_scraper(db: DatabaseInterface = Depends(get_db_client)) -> Scraper:
    return Scraper(db)


URL = "https://dentalstall.com/shop/page/"


def generate_urls(page_limit: int) -> list[str]:
    return [f"{URL}{page}" for page in range(1, page_limit + 1)]


@router.get("/")
async def scrape_route(page_limit: int = 5, scraper: Scraper = Depends(get_scraper)):
    urls = generate_urls(page_limit)
    success = await scraper.scrape_and_save(urls)
    if success:
        return {"message": "Products scraped and saved successfully"}
    else:
        return {"message": "Failed to scrape or save products"}
