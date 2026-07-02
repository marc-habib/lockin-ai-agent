"""
Tests for deterministic calculations.

Ensures all TDEE and macro calculations are accurate and reproducible.
"""

import pytest
from app.utils.calculations import (
    calculate_bmr,
    calculate_tdee,
    calculate_target_calories,
    calculate_macros,
    calculate_recipe_macros,
)
from app.models.enums import Sex, Goal, ActivityLevel


class TestBMRCalculation:
    """Test Basal Metabolic Rate calculations."""
    
    def test_bmr_male(self):
        """Test BMR for male."""
        bmr = calculate_bmr(
            age=28,
            sex=Sex.MALE,
            height_cm=180,
            weight_kg=75
        )
        # Expected: (10 * 75) + (6.25 * 180) - (5 * 28) + 5 = 1750
        assert bmr == pytest.approx(1750.0, abs=1.0)
    
    def test_bmr_female(self):
        """Test BMR for female."""
        bmr = calculate_bmr(
            age=25,
            sex=Sex.FEMALE,
            height_cm=165,
            weight_kg=60
        )
        # Expected: (10 * 60) + (6.25 * 165) - (5 * 25) - 161 = 1376.25
        assert bmr == pytest.approx(1376.3, abs=1.0)


class TestTDEECalculation:
    """Test Total Daily Energy Expenditure calculations."""
    
    def test_tdee_sedentary(self):
        """Test TDEE with sedentary activity level."""
        bmr = 1750.0
        tdee = calculate_tdee(bmr, ActivityLevel.SEDENTARY)
        # Expected: 1750 * 1.2 = 2100
        assert tdee == pytest.approx(2100.0, abs=1.0)
    
    def test_tdee_moderate(self):
        """Test TDEE with moderate activity level."""
        bmr = 1750.0
        tdee = calculate_tdee(bmr, ActivityLevel.MODERATE)
        # Expected: 1750 * 1.55 = 2712.5
        assert tdee == pytest.approx(2712.5, abs=1.0)


class TestTargetCalories:
    """Test target calorie calculations based on goals."""
    
    def test_lose_fat(self):
        """Test calorie target for fat loss."""
        tdee = 2500.0
        target = calculate_target_calories(tdee, Goal.LOSE_FAT)
        # Expected: 2500 - 500 = 2000
        assert target == 2000.0
    
    def test_maintain(self):
        """Test calorie target for maintenance."""
        tdee = 2500.0
        target = calculate_target_calories(tdee, Goal.MAINTAIN)
        # Expected: 2500 + 0 = 2500
        assert target == 2500.0
    
    def test_gain_muscle(self):
        """Test calorie target for muscle gain."""
        tdee = 2500.0
        target = calculate_target_calories(tdee, Goal.GAIN_MUSCLE)
        # Expected: 2500 + 300 = 2800
        assert target == 2800.0


class TestMacroCalculation:
    """Test macronutrient calculations."""
    
    def test_macros_lose_fat(self):
        """Test macro distribution for fat loss."""
        macros = calculate_macros(
            target_calories=2000.0,
            goal=Goal.LOSE_FAT,
            weight_kg=75.0
        )
        
        # Higher protein for fat loss (35% of calories or 2g/kg, whichever is higher)
        assert macros['protein_g'] >= 150.0  # 2g/kg * 75kg
        assert macros['carbs_g'] > 0
        assert macros['fat_g'] > 0
        
        # Total calories should match (within rounding)
        total_cals = (macros['protein_g'] * 4) + (macros['carbs_g'] * 4) + (macros['fat_g'] * 9)
        assert total_cals == pytest.approx(2000.0, abs=10.0)
    
    def test_macros_gain_muscle(self):
        """Test macro distribution for muscle gain."""
        macros = calculate_macros(
            target_calories=3000.0,
            goal=Goal.GAIN_MUSCLE,
            weight_kg=75.0
        )
        
        # Adequate protein for muscle gain (1.8g/kg minimum)
        assert macros['protein_g'] >= 135.0  # 1.8g/kg * 75kg
        assert macros['carbs_g'] > macros['fat_g']  # Higher carbs for training
        
        # Total calories should match
        total_cals = (macros['protein_g'] * 4) + (macros['carbs_g'] * 4) + (macros['fat_g'] * 9)
        assert total_cals == pytest.approx(3000.0, abs=10.0)


class TestRecipeMacros:
    """Test recipe macro calculations."""
    
    def test_simple_recipe(self):
        """Test macro calculation for a simple recipe."""
        ingredients = [
            {
                'quantity_g': 200,
                'kcal_100g': 120,
                'protein_100g': 23.0,
                'carbs_100g': 0.0,
                'fat_100g': 2.6
            },  # Chicken breast
            {
                'quantity_g': 150,
                'kcal_100g': 112,
                'protein_100g': 2.6,
                'carbs_100g': 23.5,
                'fat_100g': 0.9
            },  # Brown rice
        ]
        
        result = calculate_recipe_macros(ingredients)
        
        # Chicken: 200g = 240 kcal, 46g protein, 0g carbs, 5.2g fat
        # Rice: 150g = 168 kcal, 3.9g protein, 35.25g carbs, 1.35g fat
        # Total: 408 kcal, 49.9g protein, 35.25g carbs, 6.55g fat
        
        assert result['total_calories'] == pytest.approx(408.0, abs=1.0)
        assert result['total_protein_g'] == pytest.approx(49.9, abs=0.5)
        assert result['total_carbs_g'] == pytest.approx(35.3, abs=0.5)
        assert result['total_fat_g'] == pytest.approx(6.6, abs=0.5)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
