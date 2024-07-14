from fastapi import FastAPI

from api.routers.scrape import router as scraper_router

app = FastAPI()

app.include_router(scraper_router)


@app.get("/")
def read_root():
    return "Server is running."
