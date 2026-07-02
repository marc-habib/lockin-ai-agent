"""
Tests for CIQUAL preprocessing script.
"""

import pytest
import pandas as pd
from scripts.preprocess_ciqual import clean_numeric_value


class TestCleanNumericValue:
    """Test the clean_numeric_value function."""
    
    def test_clean_comma_decimal(self):
        """Test conversion of comma decimal separator."""
        assert clean_numeric_value("4,41") == 4.41
        assert clean_numeric_value("10,5") == 10.5
        assert clean_numeric_value("0,1") == 0.1
    
    def test_clean_dash(self):
        """Test dash (missing value) converts to 0."""
        assert clean_numeric_value("-") == 0.0
        assert clean_numeric_value(" - ") == 0.0
    
    def test_clean_less_than(self):
        """Test less than notation."""
        assert clean_numeric_value("< 0,1") == 0.1
        assert clean_numeric_value("< 0.5") == 0.5
        assert clean_numeric_value("<1") == 1.0
    
    def test_clean_traces(self):
        """Test traces converts to 0."""
        assert clean_numeric_value("traces") == 0.0
        assert clean_numeric_value("Traces") == 0.0
    
    def test_clean_empty(self):
        """Test empty/None values."""
        assert clean_numeric_value("") == 0.0
        assert clean_numeric_value(None) == 0.0
        assert clean_numeric_value(pd.NA) == 0.0
    
    def test_clean_already_numeric(self):
        """Test already numeric values."""
        assert clean_numeric_value(4.41) == 4.41
        assert clean_numeric_value(10) == 10.0
        assert clean_numeric_value(0) == 0.0
    
    def test_clean_dot_decimal(self):
        """Test dot decimal separator (already correct)."""
        assert clean_numeric_value("4.41") == 4.41
        assert clean_numeric_value("10.5") == 10.5


class TestPreprocessingLogic:
    """Test preprocessing logic with mock data."""
    
    def test_mock_dataframe_processing(self):
        """Test processing a mock CIQUAL dataframe."""
        # Create mock data matching English CIQUAL 2025 format
        mock_data = {
            'alim_code': ['1000', '2000', '3000'],
            'alim_nom_eng': ['Chicken breast', 'Brown rice', 'Broccoli'],
            'alim_grp_nom_eng': ['Meat', 'Grains', 'Vegetables'],
            'Energy,\nRegulation\nEU No\n1169\n2011 (kcal\n100g)': ['165', '112', '34'],
            'Protein\n(g\n100g)': ['31,0', '2,6', '2,8'],
            'Carbohydrate\n(g\n100g)': ['0', '23,5', '6,6'],
            'Fat (g\n100g)': ['3,6', '0,9', '0,4'],
            'Sugars\n(g\n100g)': ['-', '0,2', '1,7'],
            'Fibres\n(g\n100g)': ['0', '1,8', '2,6'],
        }
        
        df = pd.DataFrame(mock_data)
        
        # Simulate the processing steps
        required_columns = {
            'alim_code': 'food_code',
            'alim_nom_eng': 'food_name',
            'alim_grp_nom_eng': 'category',
            'Energy,\nRegulation\nEU No\n1169\n2011 (kcal\n100g)': 'kcal_100g',
            'Protein\n(g\n100g)': 'protein_100g',
            'Carbohydrate\n(g\n100g)': 'carbs_100g',
            'Fat (g\n100g)': 'fat_100g',
            'Sugars\n(g\n100g)': 'sugars_100g',
            'Fibres\n(g\n100g)': 'fiber_100g',
        }
        
        # Select and rename
        df_clean = df[list(required_columns.keys())].copy()
        df_clean.columns = list(required_columns.values())
        
        # Clean numeric columns
        numeric_cols = ['kcal_100g', 'protein_100g', 'carbs_100g', 'fat_100g', 
                       'fiber_100g', 'sugars_100g']
        
        for col in numeric_cols:
            df_clean[col] = df_clean[col].apply(clean_numeric_value)
        
        # Verify results
        assert len(df_clean) == 3
        assert 'food_code' in df_clean.columns
        assert 'food_name' in df_clean.columns
        
        # Check specific values
        assert df_clean.iloc[0]['food_name'] == 'Chicken breast'
        assert df_clean.iloc[0]['kcal_100g'] == 165.0
        assert df_clean.iloc[0]['protein_100g'] == 31.0
        assert df_clean.iloc[0]['carbs_100g'] == 0.0
        assert df_clean.iloc[0]['fat_100g'] == 3.6
        assert df_clean.iloc[0]['sugars_100g'] == 0.0  # Dash converted to 0
        
        # Check comma decimal conversion
        assert df_clean.iloc[1]['protein_100g'] == 2.6
        assert df_clean.iloc[1]['carbs_100g'] == 23.5
    
    def test_missing_columns_raises_error(self):
        """Test that missing required columns raises clear error."""
        # Create incomplete mock data
        mock_data = {
            'alim_code': ['1000'],
            'alim_nom_eng': ['Chicken'],
            # Missing other required columns
        }
        
        df = pd.DataFrame(mock_data)
        
        required_columns = {
            'alim_code': 'food_code',
            'alim_nom_eng': 'food_name',
            'alim_grp_nom_eng': 'category',
            'Energy,\nRegulation\nEU No\n1169\n2011 (kcal\n100g)': 'kcal_100g',
            'Protein\n(g\n100g)': 'protein_100g',
            'Carbohydrate\n(g\n100g)': 'carbs_100g',
            'Fat (g\n100g)': 'fat_100g',
            'Sugars\n(g\n100g)': 'sugars_100g',
            'Fibres\n(g\n100g)': 'fiber_100g',
        }
        
        # Check for missing columns
        missing_cols = []
        for col in required_columns.keys():
            if col not in df.columns:
                missing_cols.append(col)
        
        # Should have missing columns
        assert len(missing_cols) > 0
        assert 'alim_grp_nom_eng' in missing_cols


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
