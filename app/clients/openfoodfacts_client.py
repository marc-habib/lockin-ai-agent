"""
OpenFoodFacts API client for LockIn AI.

Queries the OpenFoodFacts API for packaged product nutrition data.
Includes caching to reduce API calls.
"""

import requests
from typing import List
from app.schemas.nutrition import ProductNutrition
from app.repositories.api_cache_repository import api_cache_repository
from app.config import settings


class OpenFoodFactsClient:
    """Client for querying OpenFoodFacts API."""
    
    def __init__(self, api_url: str | None = None):
        """
        Initialize OpenFoodFacts client.
        
        Args:
            api_url: Base API URL. Uses config default if None.
        """
        self.api_url = api_url or settings.openfoodfacts_api_url
        self.cache = api_cache_repository
    
    def search(self, query: str, limit: int = 5) -> List[ProductNutrition]:
        """
        Search for products matching the query.
        
        Args:
            query: Search query (product name or barcode)
            limit: Maximum number of results
        
        Returns:
            List of ProductNutrition objects
        """
        # Check cache first
        cache_key = f"search:{query}:{limit}"
        cached = self.cache.get("openfoodfacts", cache_key)
        
        if cached:
            return [ProductNutrition(**item) for item in cached]
        
        # Make API request
        try:
            url = f"{self.api_url}/search"
            params = {
                "search_terms": query,
                "page_size": limit,
                "fields": "product_name,brands,nutriments,ingredients_text,allergens,nutriscore_grade,nova_group"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            products = []
            
            for product in data.get("products", [])[:limit]:
                try:
                    nutrition = self._parse_product(product)
                    if nutrition:
                        products.append(nutrition)
                except Exception:
                    # Skip products with parsing errors
                    continue
            
            # Cache results
            self.cache.set("openfoodfacts", cache_key, [p.model_dump() for p in products])
            
            return products
        
        except Exception as e:
            # Return empty list on error (API might be down)
            return []
    
    def get_by_barcode(self, barcode: str) -> ProductNutrition | None:
        """
        Get product by barcode.
        
        Args:
            barcode: Product barcode
        
        Returns:
            ProductNutrition object or None if not found
        """
        # Check cache
        cached = self.cache.get("openfoodfacts", f"barcode:{barcode}")
        
        if cached:
            return ProductNutrition(**cached)
        
        # Make API request
        try:
            url = f"{self.api_url}/product/{barcode}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("status") != 1:
                return None
            
            product = data.get("product", {})
            nutrition = self._parse_product(product)
            
            if nutrition:
                # Cache result
                self.cache.set("openfoodfacts", f"barcode:{barcode}", nutrition.model_dump())
            
            return nutrition
        
        except Exception:
            return None
    
    def _parse_product(self, product: dict) -> ProductNutrition | None:
        """
        Parse product data from API response.
        
        Args:
            product: Product dictionary from API
        
        Returns:
            ProductNutrition object or None if parsing fails
        """
        try:
            nutriments = product.get("nutriments", {})
            
            # Extract nutrition data (per 100g)
            nutrition = ProductNutrition(
                product_name=product.get("product_name", "Unknown"),
                brand=product.get("brands", "").split(",")[0].strip() if product.get("brands") else None,
                kcal_100g=float(nutriments.get("energy-kcal_100g", 0)),
                protein_100g=float(nutriments.get("proteins_100g", 0)),
                carbs_100g=float(nutriments.get("carbohydrates_100g", 0)),
                fat_100g=float(nutriments.get("fat_100g", 0)),
                fiber_100g=float(nutriments.get("fiber_100g", 0)) if nutriments.get("fiber_100g") else None,
                sugars_100g=float(nutriments.get("sugars_100g", 0)) if nutriments.get("sugars_100g") else None,
                ingredients=self._parse_ingredients(product.get("ingredients_text", "")),
                allergens=self._parse_allergens(product.get("allergens", "")),
                nutriscore=product.get("nutriscore_grade", "").upper() or None,
                nova_group=int(product.get("nova_group", 0)) if product.get("nova_group") else None,
            )
            
            return nutrition
        
        except (ValueError, KeyError):
            return None
    
    def _parse_ingredients(self, ingredients_text: str) -> List[str]:
        """
        Parse ingredients text into list.
        
        Args:
            ingredients_text: Comma-separated ingredients
        
        Returns:
            List of ingredient names
        """
        if not ingredients_text:
            return []
        
        # Split by comma and clean
        ingredients = [i.strip() for i in ingredients_text.split(",")]
        return [i for i in ingredients if i][:10]  # Limit to first 10
    
    def _parse_allergens(self, allergens_text: str) -> List[str]:
        """
        Parse allergens text into list.
        
        Args:
            allergens_text: Allergens string
        
        Returns:
            List of allergen names
        """
        if not allergens_text:
            return []
        
        # Remove "en:" prefix and split
        allergens = allergens_text.replace("en:", "").split(",")
        return [a.strip() for a in allergens if a.strip()]


# Global client instance
openfoodfacts_client = OpenFoodFactsClient()
