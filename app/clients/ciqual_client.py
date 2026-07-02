"""
CIQUAL client for LockIn AI.

Reads and searches the preprocessed CIQUAL CSV file for food nutrition data.
"""

import csv
from pathlib import Path
from typing import List
from app.schemas.nutrition import FoodNutrition


class CIQUALClient:
    """Client for querying CIQUAL nutrition database."""
    
    def __init__(self, csv_path: str = "data/ciqual_clean.csv"):
        """
        Initialize CIQUAL client.
        
        Args:
            csv_path: Path to preprocessed CIQUAL CSV file
        """
        self.csv_path = Path(csv_path)
        self._data: List[dict] | None = None
    
    def _load_data(self) -> List[dict]:
        """
        Load CIQUAL data from CSV.
        
        Returns:
            List of food dictionaries
        """
        if self._data is not None:
            return self._data
        
        if not self.csv_path.exists():
            raise FileNotFoundError(
                f"CIQUAL CSV not found: {self.csv_path}. "
                "Run scripts/preprocess_ciqual.py first."
            )
        
        self._data = []
        
        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert numeric fields
                try:
                    self._data.append({
                        'food_name': row['food_name'],
                        'category': row.get('category', ''),
                        'kcal_100g': float(row.get('kcal_100g', 0)),
                        'protein_100g': float(row.get('protein_100g', 0)),
                        'carbs_100g': float(row.get('carbs_100g', 0)),
                        'fat_100g': float(row.get('fat_100g', 0)),
                        'fiber_100g': float(row.get('fiber_100g', 0)),
                        'sugars_100g': float(row.get('sugars_100g', 0)),
                    })
                except (ValueError, KeyError) as e:
                    # Skip malformed rows
                    continue
        
        return self._data
    
    def search(self, query: str, limit: int = 5) -> List[FoodNutrition]:
        """
        Search for foods matching the query.
        
        Args:
            query: Search query (food name)
            limit: Maximum number of results
        
        Returns:
            List of FoodNutrition objects
        """
        data = self._load_data()
        query_lower = query.lower().strip()
        
        # Find matches (case-insensitive substring search)
        matches = []
        for food in data:
            if query_lower in food['food_name'].lower():
                matches.append(
                    FoodNutrition(
                        food_name=food['food_name'],
                        category=food['category'],
                        kcal_100g=food['kcal_100g'],
                        protein_100g=food['protein_100g'],
                        carbs_100g=food['carbs_100g'],
                        fat_100g=food['fat_100g'],
                        fiber_100g=food['fiber_100g'],
                        sugars_100g=food['sugars_100g'],
                        source="ciqual"
                    )
                )
                
                if len(matches) >= limit:
                    break
        
        return matches
    
    def get_by_name(self, food_name: str) -> FoodNutrition | None:
        """
        Get exact food by name.
        
        Args:
            food_name: Exact food name
        
        Returns:
            FoodNutrition object or None if not found
        """
        data = self._load_data()
        
        for food in data:
            if food['food_name'].lower() == food_name.lower():
                return FoodNutrition(
                    food_name=food['food_name'],
                    category=food['category'],
                    kcal_100g=food['kcal_100g'],
                    protein_100g=food['protein_100g'],
                    carbs_100g=food['carbs_100g'],
                    fat_100g=food['fat_100g'],
                    fiber_100g=food['fiber_100g'],
                    sugars_100g=food['sugars_100g'],
                    source="ciqual"
                )
        
        return None


# Global client instance
ciqual_client = CIQUALClient()
