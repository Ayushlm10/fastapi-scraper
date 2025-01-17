At a high level , this is the architecture:

![alt text](arch.png)

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
- We are not sending requests one by one. We are using **httpx** library to send requests to all urls concurrently leaving **asyncio's** event loop to handle and collect the results whenever they are available.

**Testing**

Assuming the setup is done.

1) Start the redis-server , (optionally redis-cli to see the cache updates)
2) Start the fast api web server: `fastapi dev main.py`
3) Send a curl request:
```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/scrape/?page_limit=2' \
  -H 'accept: application/json' \
  -H 'access_token: abcde'
```
-> This will scrape the first two pages. Note access_token is _abcde_. 
Output (notification service also prints to the console): 

![image](https://github.com/user-attachments/assets/2b82978e-91f5-4d42-bdf2-78a5ae418a84)

4) Malformed credentials (returns 403):

![image](https://github.com/user-attachments/assets/80d29dd2-ba4d-4a32-b704-36a3833ab9ba)

6) If we again send a request to fetch the first page, it will see it is present in the cache and not hit the db.
```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/scrape/?page_limit=1' \
  -H 'accept: application/json' \
  -H 'access_token: abcde'
```
![image](https://github.com/user-attachments/assets/c7b4407c-9e5a-4917-9484-a22d991d15fc)

As we can see , 0 products were updated in the db.

7) A saved product has this structure (can be seen in products.json). Final data will be a list of these products.:
```json
{
    "product_title": "1 x GDC Extraction Forceps Lo...",
    "product_price": 850.0,
    "path_to_image": "https://dentalstall.com/wp-content/uploads/2021/11/GDC-Extraction-Forceps-Lower-Molars-86A-Standard-FX86AS-300x300.jpg"
},
```
