"""
Tool descriptions for function calling.

Provides clear descriptions of each tool's purpose and usage.
"""


TOOL_DESCRIPTIONS = {
    "food_lookup": {
        "name": "food_lookup",
        "description": "Search for generic food nutrition data from the CIQUAL database. Use this for whole foods like fruits, vegetables, meats, grains, etc. Returns nutrition per 100g.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Food name to search for (e.g., 'chicken breast', 'banana', 'oats')"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    },
    
    "product_lookup": {
        "name": "product_lookup",
        "description": "Search for packaged product nutrition data from OpenFoodFacts. Use this for branded products, packaged foods, or when you need allergen/ingredient information. Returns nutrition per 100g plus NutriScore and NOVA group.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Product name or barcode to search for"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    },
    
    "recipe_macro": {
        "name": "recipe_macro",
        "description": "Calculate total macros for a recipe from its ingredients. Use this when you need to calculate nutrition for a complete dish or meal. Requires nutrition data per 100g for each ingredient.",
        "parameters": {
            "type": "object",
            "properties": {
                "recipe_name": {
                    "type": "string",
                    "description": "Name of the recipe (optional)"
                },
                "ingredients": {
                    "type": "array",
                    "description": "List of ingredients with their quantities and nutrition per 100g",
                    "items": {
                        "type": "object",
                        "properties": {
                            "food_name": {"type": "string"},
                            "quantity_g": {"type": "number"},
                            "kcal_100g": {"type": "number"},
                            "protein_100g": {"type": "number"},
                            "carbs_100g": {"type": "number"},
                            "fat_100g": {"type": "number"}
                        },
                        "required": ["food_name", "quantity_g", "kcal_100g", "protein_100g", "carbs_100g", "fat_100g"]
                    }
                }
            },
            "required": ["ingredients"]
        }
    },
    
    "daily_planner": {
        "name": "daily_planner",
        "description": "Generate a complete daily meal plan based on the user's targets and preferences. Use this when the user asks to plan their meals for the day. The planner will automatically use the user's profile targets.",
        "parameters": {
            "type": "object",
            "properties": {
                "target_calories": {
                    "type": "number",
                    "description": "Target daily calories"
                },
                "target_protein_g": {
                    "type": "number",
                    "description": "Target daily protein in grams"
                },
                "target_carbs_g": {
                    "type": "number",
                    "description": "Target daily carbs in grams"
                },
                "target_fat_g": {
                    "type": "number",
                    "description": "Target daily fat in grams"
                },
                "num_meals": {
                    "type": "integer",
                    "description": "Number of meals per day (2-6)",
                    "default": 3
                },
                "preferences": {
                    "type": "object",
                    "description": "User preferences including allergies, restrictions, and dislikes",
                    "properties": {
                        "allergies": {"type": "array", "items": {"type": "string"}},
                        "dietary_restrictions": {"type": "array", "items": {"type": "string"}},
                        "disliked_foods": {"type": "array", "items": {"type": "string"}}
                    }
                }
            },
            "required": ["target_calories", "target_protein_g", "target_carbs_g", "target_fat_g"]
        }
    },
    
    "get_progress": {
        "name": "get_progress",
        "description": "Get the user's nutrition progress for today. Use this when the user asks about their remaining calories, protein, or whether they're on track. Returns consumed and remaining macros.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "User identifier"
                }
            },
            "required": ["user_id"]
        }
    }
}


def get_tool_schema(tool_name: str) -> dict:
    """
    Get the schema for a specific tool.
    
    Args:
        tool_name: Name of the tool
    
    Returns:
        Tool schema dict
    """
    return TOOL_DESCRIPTIONS.get(tool_name, {})


def get_all_tool_schemas() -> list[dict]:
    """
    Get all tool schemas.
    
    Returns:
        List of tool schema dicts
    """
    return list(TOOL_DESCRIPTIONS.values())
