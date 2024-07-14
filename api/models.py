from pydantic import BaseModel


class Product(BaseModel):
    name: str
    price: str
    image_link: str


class ScrapedProducts(BaseModel):
    products: list[Product]
