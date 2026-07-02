"""
Pytest configuration and fixtures for LockIn AI tests.
"""

import pytest
from datetime import datetime
from app.schemas.profile import ProfileResponse, MacroTargets
from app.models.enums import Sex, Goal, ActivityLevel


@pytest.fixture
def sample_profile():
    """Create a sample profile for testing."""
    return ProfileResponse(
        user_id="test_user",
        age=25,
        sex=Sex.MALE,
        height_cm=180,
        weight_kg=75,
        goal=Goal.MAINTAIN,
        activity_level=ActivityLevel.MODERATE,
        gym_sessions_per_week=4,
        running_sessions_per_week=2,
        allergies=[],
        dietary_restrictions=[],
        disliked_foods=[],
        country="US",
        budget_per_day=50.0,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        bmr=1750.0,
        tdee=2700.0,
        target_macros=MacroTargets(
            calories=2700.0,
            protein_g=135.0,
            carbs_g=300.0,
            fat_g=75.0
        )
    )


@pytest.fixture
def sample_profile_with_peanut_allergy():
    """Create a sample profile with peanut allergy for testing."""
    return ProfileResponse(
        user_id="test_user_allergy",
        age=28,
        sex=Sex.FEMALE,
        height_cm=165,
        weight_kg=60,
        goal=Goal.LOSE_FAT,
        activity_level=ActivityLevel.LIGHT,
        gym_sessions_per_week=3,
        running_sessions_per_week=1,
        allergies=["peanuts"],
        dietary_restrictions=[],
        disliked_foods=[],
        country="US",
        budget_per_day=40.0,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        bmr=1400.0,
        tdee=2100.0,
        target_macros=MacroTargets(
            calories=1600.0,
            protein_g=120.0,
            carbs_g=150.0,
            fat_g=45.0
        )
    )
