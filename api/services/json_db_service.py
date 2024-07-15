import json
import os
from typing import Dict, List

from interfaces.database_interface import DatabaseInterface


class JSONDatabaseService(DatabaseInterface):
    def __init__(self, file_path: str):
        self.file_path = file_path

    def _flatten_to_dict(self, products: list):
        flat_products = [product for sublist in products for product in sublist]
        product_dicts = [product.dict() for product in flat_products]
        return product_dicts

    async def add_products(self, products: List[Dict[str, str]]) -> bool:
        existing_products = await self.get_all_products()
        existing_dict = {p["product_title"]: p for p in existing_products}
        new_products = self._flatten_to_dict(products)
        updated = False

        for product in new_products:
            if product["product_title"] in existing_dict:
                if existing_dict[product["product_title"]] != product:
                    existing_dict[product["product_title"]] = product
                    updated = True
            else:
                existing_dict[product["product_title"]] = product
                updated = True

        if updated:
            return await self._save_products(list(existing_dict.values()))
        return True

    async def get_all_products(self) -> List[Dict[str, str]]:
        if not os.path.exists(self.file_path):
            return []
        with open(self.file_path, "r") as f:
            return json.load(f)

    async def clear_all_products(self) -> bool:
        await self.cache.clear_cache()
        return await self._save_products([])

    async def _save_products(self, products: List[Dict[str, str]]) -> bool:
        try:
            with open(self.file_path, "w") as f:
                json.dump(products, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving products: {e}")
            return False
