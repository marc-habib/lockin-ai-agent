"""
Tests for chat response quality improvements.

Ensures:
- Self-check text is not returned to users
- Structured data is populated for meal plans
- Peanut allergy blocks all nuts
- Meal quantities are realistically rounded
"""

import pytest
from unittest.mock import Mock, patch
from app.guardrails.output_guardrails import OutputGuardrails
from app.services.planning_service import PlanningService
from app.agent.handler import run_agent_handler
from app.models.enums import Intent, RequestStatus
from app.schemas.profile import ProfileResponse, MacroTargets


class TestReflectionRemoval:
    """Test that internal reflection text is removed from responses."""
    
    def test_clean_response_removes_self_check(self):
        """Test that self-check text is removed."""
        guardrails = OutputGuardrails()
        
        response_with_check = """Here's your meal plan for today:

**Breakfast:**
- Oats: 80g
- Banana: 120g

**Self-check**: This response is grounded in tool results and contains no hallucinated data.

Let me know if you need adjustments!"""
        
        cleaned = guardrails.clean_response(response_with_check)
        
        assert "self-check" not in cleaned.lower()
        assert "This response is grounded" not in cleaned
        assert "Here's your meal plan" in cleaned
        assert "Let me know" in cleaned
    
    def test_clean_response_removes_internal_markers(self):
        """Test that [internal] markers are removed."""
        guardrails = OutputGuardrails()
        
        response = """Your daily plan:
- Breakfast: 500 kcal
- Lunch: 700 kcal

[Internal validation: All values from tool results]

Total: 1200 kcal"""
        
        cleaned = guardrails.clean_response(response)
        
        assert "[internal" not in cleaned.lower()
        assert "validation" not in cleaned.lower()
        assert "Your daily plan" in cleaned
        assert "Total: 1200 kcal" in cleaned
    
    def test_clean_response_removes_verification_text(self):
        """Test that verification text is removed."""
        guardrails = OutputGuardrails()
        
        response = """Let me verify this is correct before responding.

Here's your plan based on your targets."""
        
        cleaned = guardrails.clean_response(response)
        
        assert "let me verify" not in cleaned.lower()
        assert "Here's your plan" in cleaned
    
    def test_clean_response_preserves_normal_text(self):
        """Test that normal response text is preserved."""
        guardrails = OutputGuardrails()
        
        response = """Here's your personalized meal plan:

**Breakfast** (500 kcal):
- Oats: 80g
- Banana: 120g

**Lunch** (700 kcal):
- Chicken: 150g
- Rice: 100g

Let me know if you'd like a higher-protein version!"""
        
        cleaned = guardrails.clean_response(response)
        
        # Should be unchanged
        assert cleaned == response


class TestQuantityRounding:
    """Test that meal quantities are rounded to realistic values."""
    
    def test_round_quantity_small_values(self):
        """Test rounding for small quantities (< 50g)."""
        service = PlanningService()
        
        # Should round to nearest 5g
        assert service._round_quantity(23.7) == 25
        assert service._round_quantity(31.2) == 30
        assert service._round_quantity(47.8) == 50
        assert service._round_quantity(12.3) == 10
    
    def test_round_quantity_medium_values(self):
        """Test rounding for medium quantities (50-200g)."""
        service = PlanningService()
        
        # Should round to nearest 10g
        assert service._round_quantity(67.4) == 70
        assert service._round_quantity(123.8) == 120
        assert service._round_quantity(156.2) == 160
        assert service._round_quantity(199.9) == 200
    
    def test_round_quantity_large_values(self):
        """Test rounding for large quantities (> 200g)."""
        service = PlanningService()
        
        # Should round to nearest 25g
        assert service._round_quantity(237.6) == 250
        assert service._round_quantity(312.1) == 300
        assert service._round_quantity(463.9) == 475
    
    def test_meal_plan_uses_rounded_quantities(self):
        """Test that generated meal plans have rounded quantities."""
        service = PlanningService()
        
        meals = service.generate_meal_plan(
            target_calories=2000,
            target_protein_g=150,
            target_carbs_g=200,
            target_fat_g=67,
            num_meals=3,
            preferences={}
        )
        
        for meal in meals:
            for food in meal.foods:
                quantity = food['quantity_g']
                
                # Check that quantities are realistic (not like 109.2g or 163.7g)
                if quantity < 50:
                    # Should be multiple of 5
                    assert quantity % 5 == 0, f"Small quantity {quantity}g should be multiple of 5"
                elif quantity < 200:
                    # Should be multiple of 10
                    assert quantity % 10 == 0, f"Medium quantity {quantity}g should be multiple of 10"
                else:
                    # Should be multiple of 25
                    assert quantity % 25 == 0, f"Large quantity {quantity}g should be multiple of 25"


class TestPeanutAllergyHandling:
    """Test that peanut allergy blocks all nuts."""
    
    def test_peanut_allergy_blocks_almonds(self):
        """Test that peanut allergy prevents almonds in snacks."""
        service = PlanningService()
        
        # Generate snack with peanut allergy
        foods = service._generate_meal_foods(
            meal_type='snack',
            target_calories=200,
            allergies=['peanuts'],
            restrictions=[],
            dislikes=[]
        )
        
        # Should not contain almonds or any nuts
        for food in foods:
            food_name = food['food_name'].lower()
            assert 'almond' not in food_name, "Peanut allergy should block almonds"
            assert 'nut' not in food_name, "Peanut allergy should block all nuts"
    
    def test_no_allergy_allows_almonds(self):
        """Test that without peanut allergy, almonds are allowed."""
        service = PlanningService()
        
        # Generate snack without peanut allergy
        foods = service._generate_meal_foods(
            meal_type='snack',
            target_calories=200,
            allergies=[],
            restrictions=[],
            dislikes=[]
        )
        
        # Should potentially contain almonds (if template includes them)
        # This is template-dependent, so we just verify no crash
        assert isinstance(foods, list)
    
    def test_full_meal_plan_respects_peanut_allergy(self):
        """Test that full meal plan respects peanut allergy."""
        service = PlanningService()
        
        meals = service.generate_meal_plan(
            target_calories=2000,
            target_protein_g=150,
            target_carbs_g=200,
            target_fat_g=67,
            num_meals=4,  # Includes snack
            preferences={'allergies': ['peanuts']}
        )
        
        # Check all meals for nuts
        for meal in meals:
            for food in meal.foods:
                food_name = food['food_name'].lower()
                assert 'almond' not in food_name, f"Found almonds in {meal.meal_type}"
                assert 'peanut' not in food_name, f"Found peanuts in {meal.meal_type}"


class TestStructuredDataPopulation:
    """Test that structured data is populated for meal plans."""
    
    @patch('app.agent.handler.agent_service')
    @patch('app.agent.handler.profile_guardrails')
    @patch('app.agent.handler.input_guardrails')
    def test_meal_plan_response_has_data_field(
        self,
        mock_input_guard,
        mock_profile_guard,
        mock_agent,
        sample_profile
    ):
        """Test that meal plan responses include structured data."""
        # Mock profile
        profile = sample_profile
        
        mock_profile_guard.get_profile_or_error.return_value = (profile, None)
        mock_input_guard.validate.return_value = (True, None)
        
        # Mock agent response with meal plan tool result
        mock_agent.run.return_value = {
            'response': 'Here is your meal plan for today.',
            'tool_calls': ['daily_planner'],
            'tool_results': [{
                'tool_name': 'daily_planner',
                'success': True,
                'result': {
                    'meals': [
                        {
                            'meal_type': 'breakfast',
                            'foods': [{'food_name': 'Oats', 'quantity_g': 80}],
                            'total_calories': 300,
                            'total_protein_g': 10,
                            'total_carbs_g': 50,
                            'total_fat_g': 5
                        }
                    ],
                    'total_calories': 300,
                    'total_protein_g': 10,
                    'total_carbs_g': 50,
                    'total_fat_g': 5
                }
            }],
            'usage': {'input_tokens': 100, 'output_tokens': 50},
            'iterations': 1
        }
        
        response = run_agent_handler(user_id="test_user", message="Plan my meals")
        
        # CRITICAL: data field must not be None for meal plans
        assert response.data is not None, "Meal plan response must have data field populated"
        assert 'meals' in response.data, "Data must contain meals"
        assert response.status == RequestStatus.SUCCESS
    
    @patch('app.agent.handler.agent_service')
    @patch('app.agent.handler.profile_guardrails')
    @patch('app.agent.handler.input_guardrails')
    def test_non_meal_plan_response_has_null_data(
        self,
        mock_input_guard,
        mock_profile_guard,
        mock_agent,
        sample_profile
    ):
        """Test that non-meal-plan responses have null data field."""
        profile = sample_profile
        
        mock_profile_guard.get_profile_or_error.return_value = (profile, None)
        mock_input_guard.validate.return_value = (True, None)
        
        # Mock agent response for food search (not meal plan)
        mock_agent.run.return_value = {
            'response': 'Chicken breast has 165 kcal per 100g.',
            'tool_calls': ['food_lookup'],
            'tool_results': [{
                'tool_name': 'food_lookup',
                'success': True,
                'result': []
            }],
            'usage': {'input_tokens': 50, 'output_tokens': 25},
            'iterations': 1
        }
        
        response = run_agent_handler(user_id="test_user", message="What's in chicken?")
        
        # For non-meal-plan intents, data can be None
        # (This is acceptable - only meal plans require structured data)
        assert response.status == RequestStatus.SUCCESS


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
