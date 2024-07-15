import aioredis
from fastapi import APIRouter, Depends, Query

from api.dependencies import get_api_key
from api.services.console_notification_service import ConsoleNotificationStrategy
from api.services.json_db_service import JSONDatabaseService
from api.services.redis_cache_service import RedisCacheService
from interfaces.cache_interface import CacheInterface
from interfaces.database_interface import DatabaseInterface
from interfaces.notifications_interface import NotificationsInterface
from scraper.scraper_service import ScraperService as Scraper

URL = "https://dentalstall.com/shop/page/"  # should we pass it from cmd line?

router = APIRouter(
    prefix="/scrape",
)


def get_db_client() -> DatabaseInterface:
    """
    This will serve as the db client. We can swap out the database implementation easily without changing the code.
    """
    return JSONDatabaseService("products.json")


def get_notification_strategy() -> NotificationsInterface:
    """
    This will serve as the notification strategy.
    We can swap out the notification service implementation easily without changing the code.
    """
    return ConsoleNotificationStrategy()


async def get_cache_service() -> CacheInterface:
    """
    This will serve as the cache service. We can swap out the cache implementation easily without changing the code.
    """
    redis_url = "redis://localhost:6379"
    try:
        client = aioredis.from_url(redis_url)
        await client.ping()
        return RedisCacheService(redis_url=redis_url)
    except aioredis.ConnectionError:
        return None


async def get_scraper(
    db: DatabaseInterface = Depends(get_db_client),
    notifications=Depends(get_notification_strategy),
    cache_service=Depends(get_cache_service),
) -> Scraper:
    return Scraper(db, notifications, cache=cache_service)


def generate_urls(page_limit: int) -> list[str]:
    return [f"{URL}{page}" for page in range(1, page_limit + 1)]


@router.get("/")
async def scrape_route(
    page_limit: int = 5,
    scraper: Scraper = Depends(get_scraper),
    proxy: str = Query(None),
    api_key: str = Depends(get_api_key),
):
    urls = generate_urls(page_limit)
    success = await scraper.scrape_and_save(urls, proxy)
    if success:
        return {"message": "Products scraped and saved successfully"}
    else:
        return {"message": "Failed to scrape or save products"}


@router.post("/clear")
async def clear_all_products(scraper: Scraper = Depends(get_scraper), api_key: str = Depends(get_api_key)):
    success = await scraper.clear_products()
    if success:
        return {"message": "All products cleared successfully"}
    else:
        return {"message": "Failed to clear products"}


@router.get("/get_all_products")
async def get_all_products(scraper: Scraper = Depends(get_scraper), api_key: str = Depends(get_api_key)):
    success = await scraper.get_all_products()
    return success
