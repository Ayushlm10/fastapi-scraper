At a high level , this is the architecture:

![alt text](image-1.png)

Features:

- Scrape product information: Scrapes product name, price, and image from each page of the catalogue using **beautiful soup**.
- Page limit setting: Option to limit the number of pages to scrape.
- Proxy support: Option to provide a proxy string for scraping.
- Caching: **Redis** for caching with option to use fit in any other strategy.
- Notifications: Sends notifications about the scraping status (number of products scraped and updated).
- Simple authentication: Protects the scraping endpoint with a static API key.
- Uses **ruff** for formatting and linting.
- Data and type validation using **pydantic**.

Setup:

- Setup [poetry](https://python-poetry.org/docs/#installation).
- `poetry install`
- `poetry shell`
- `fastapi dev main.py`

Code is written in a way that even if a redis server is not running, it will stil be able to run.
So optionally we can set a redis server now running on port 6379 (url can be configured in `api/routers/scrape.py`).

Access token is static and set to `abcde`.
Following endpoints are available:

1. Scrape with page limit: `http://localhost:8000/scrape?page_limit=2` (by default page_limit is set to 5)

```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/scrape/?page_limit=2' \
  -H 'accept: application/json' \
  -H 'access_token: abcde'
```

2. Clear database (and cache):

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/scrape/clear' \
  -H 'accept: application/json' \
  -H 'access_token: abcde'
```

- For this particular implementation , final data is stored in a json file `products.json` present in the root.

Implementation details:

Everything is designed to be configurable. Database to be used , Notification strategy, cache etc.

Everything follows this model (Taking example of database here):

- Create an interface(`interfaces/database_interface.py`) with the required abstract methods. For a class to be of this type it has to implement **all** the methods defined in the interface.
- In `api/services`, we have implementations of these interfaces. In case of database interface we have the `json_db_interface.py` class which implements all methods defined by the the database interface.
- In the main router , `api/router/scraper.py` we inject all the dependencies and pass to the scraper service which is responsible for the main scraping logic and its interaction with the database and cache.
- This way we can create any class (postgres, mysql, dynamodb, etc) which implements the database interface and then from the main router we can inject that particular dependency to be passed to the scraper service and achieve an easy way to use any other database/notification strategy/cache easily.
