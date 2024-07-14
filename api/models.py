from pydantic import BaseModel


class Product(BaseModel):
    product_title: str
    product_price: str
    path_to_image: str


class ScrapedProducts(BaseModel):
    products: list[Product]
