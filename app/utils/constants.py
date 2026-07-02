"""
Constants for LockIn AI.

Contains all magic numbers, multipliers, and formulas used in calculations.
All values are based on established nutritional science and fitness research.
"""

from app.models.enums import ActivityLevel, Goal

# Activity Level Multipliers for TDEE
# Based on the Mifflin-St Jeor equation with activity factors
ACTIVITY_MULTIPLIERS = {
    ActivityLevel.SEDENTARY: 1.2,
    ActivityLevel.LIGHT: 1.375,
    ActivityLevel.MODERATE: 1.55,
    ActivityLevel.ACTIVE: 1.725,
    ActivityLevel.VERY_ACTIVE: 1.9,
}

# Goal-based calorie adjustments (relative to TDEE)
GOAL_CALORIE_ADJUSTMENTS = {
    Goal.LOSE_FAT: -500,  # 500 calorie deficit for ~0.5kg/week loss
    Goal.MAINTAIN: 0,  # Maintain current weight
    Goal.GAIN_MUSCLE: 300,  # 300 calorie surplus for lean muscle gain
}

# Macro distribution by goal (protein, carbs, fat as % of calories)
# Based on evidence-based nutrition guidelines
MACRO_DISTRIBUTIONS = {
    Goal.LOSE_FAT: {
        "protein_pct": 0.35,  # Higher protein to preserve muscle
        "fat_pct": 0.25,
        "carbs_pct": 0.40,
    },
    Goal.MAINTAIN: {
        "protein_pct": 0.30,
        "fat_pct": 0.25,
        "carbs_pct": 0.45,
    },
    Goal.GAIN_MUSCLE: {
        "protein_pct": 0.30,
        "fat_pct": 0.25,
        "carbs_pct": 0.45,  # Higher carbs for training energy
    },
}

# Calories per gram of macronutrient
CALORIES_PER_GRAM = {
    "protein": 4,
    "carbs": 4,
    "fat": 9,
}

# Minimum protein intake (g/kg body weight) by goal
MIN_PROTEIN_PER_KG = {
    Goal.LOSE_FAT: 2.0,  # Higher during deficit to preserve muscle
    Goal.MAINTAIN: 1.6,
    Goal.GAIN_MUSCLE: 1.8,
}

# Maximum message length for input validation
MAX_MESSAGE_LENGTH = 2000

# Maximum reasoning steps to prevent infinite loops
MAX_REASONING_STEPS = 5

# Cache expiry (days)
DEFAULT_CACHE_EXPIRY_DAYS = 30

# Dangerous keywords for safety guardrails
MEDICAL_KEYWORDS = [
    "diagnose", "diagnosis", "cure", "treat", "treatment", "disease",
    "medicine", "medicines", "medication", "prescription", "prescribe", "prescribed",
    "pill", "pills", "drug", "drugs", "dosage", "dose",
    "painkiller", "painkillers", "antibiotic", "antibiotics",
    "ibuprofen", "paracetamol", "aspirin",
    "doctor", "physician", "medical advice",
    "steroids", "anabolic", "testosterone", "hgh", "growth hormone",
    "clenbuterol", "dnp", "injury", "pain", "surgery"
]

# Prompt injection patterns
INJECTION_PATTERNS = [
    "ignore previous instructions",
    "ignore all previous",
    "disregard previous",
    "forget previous",
    "new instructions",
    "system:",
    "assistant:",
    "you are now",
    "act as",
    "pretend to be",
]

# Tool execution timeout (seconds)
TOOL_TIMEOUT_SECONDS = 30

# LLM cost estimation (USD per 1M tokens)
# Approximate costs as of 2024
LLM_COSTS = {
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4-turbo": {"input": 10.00, "output": 30.00},
    "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
    "claude-3-5-haiku-20241022": {"input": 0.80, "output": 4.00},
    "gemini-2.0-flash-exp": {"input": 0.00, "output": 0.00},  # Free tier
    "gemini-1.5-pro": {"input": 1.25, "output": 5.00},
}

# CIQUAL CSV columns
CIQUAL_COLUMNS = [
    "food_name",
    "category",
    "kcal_100g",
    "protein_100g",
    "carbs_100g",
    "fat_100g",
    "fiber_100g",
    "sugars_100g",
]
