"""
CIQUAL data preprocessing script.

Converts the official English CIQUAL 2025 Excel file into a clean CSV.

Usage:
    python scripts/preprocess_ciqual.py

Input: data/ciqual.xlsx (English CIQUAL 2025 from https://ciqual.anses.fr/)
Output: data/ciqual_clean.csv
"""

import pandas as pd
import re
from pathlib import Path


def clean_numeric_value(value) -> float:
    """
    Clean CIQUAL numeric values.
    
    CIQUAL uses:
    - Comma as decimal separator: "4,41" -> 4.41
    - Dash for missing: "-" -> 0.0
    - Less than notation: "< 0,1" -> 0.1
    - Traces: "traces" -> 0.0
    
    Args:
        value: Raw value from CIQUAL
    
    Returns:
        Cleaned float value
    """
    if pd.isna(value):
        return 0.0
    
    if isinstance(value, (int, float)):
        return float(value)
    
    value_str = str(value).strip().lower()
    
    # Handle dash (missing value)
    if value_str == '-' or value_str == '':
        return 0.0
    
    # Handle traces
    if 'trace' in value_str:
        return 0.0
    
    # Handle "< X" notation
    if value_str.startswith('<'):
        # Extract number after <
        match = re.search(r'[\d,\.]+', value_str)
        if match:
            num_str = match.group().replace(',', '.')
            return float(num_str)
        return 0.1  # Default for "< something"
    
    # Replace comma with dot for decimal
    value_str = value_str.replace(',', '.')
    
    # Extract first number found
    match = re.search(r'[\d\.]+', value_str)
    if match:
        try:
            return float(match.group())
        except ValueError:
            return 0.0
    
    return 0.0


def preprocess_ciqual(
    input_path: str = "data/ciqual.xlsx",
    output_path: str = "data/ciqual_clean.csv"
) -> None:
    """
    Preprocess English CIQUAL 2025 data.
    
    Args:
        input_path: Path to input Excel file
        output_path: Path to output CSV file
    """
    print(f"Reading CIQUAL data from {input_path}...")
    
    try:
        # Read the Excel file - English CIQUAL 2025 uses "food composition" sheet
        df = pd.read_excel(input_path, sheet_name="food composition")
        
        print(f"Loaded {len(df)} rows")
        print(f"Columns found: {list(df.columns)}")
        
        # Define exact column names for English CIQUAL 2025
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
        
        # Check that all required columns exist
        missing_cols = []
        for col in required_columns.keys():
            if col not in df.columns:
                missing_cols.append(col)
        
        if missing_cols:
            raise ValueError(
                f"Missing required columns in CIQUAL file:\n"
                f"{missing_cols}\n\n"
                f"Expected English CIQUAL 2025 format with sheet 'food composition'.\n"
                f"Available columns: {list(df.columns)}"
            )
        
        # Select and rename columns
        df_clean = df[list(required_columns.keys())].copy()
        df_clean.columns = list(required_columns.values())
        
        # Drop rows without food name
        df_clean = df_clean.dropna(subset=['food_name'])
        df_clean = df_clean[df_clean['food_name'].str.strip() != '']
        
        # Clean numeric columns using the clean_numeric_value function
        numeric_cols = ['kcal_100g', 'protein_100g', 'carbs_100g', 'fat_100g', 
                       'fiber_100g', 'sugars_100g']
        
        for col in numeric_cols:
            df_clean[col] = df_clean[col].apply(clean_numeric_value)
        
        # Remove duplicates
        df_clean = df_clean.drop_duplicates(subset=['food_name'])
        
        # Sort by food name
        df_clean = df_clean.sort_values('food_name')
        
        # Save to CSV
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        df_clean.to_csv(output_path, index=False, encoding='utf-8')
        
        print(f"\nPreprocessing complete!")
        print(f"Output: {output_path}")
        print(f"Rows: {len(df_clean)}")
        print(f"Columns: {list(df_clean.columns)}")
        print(f"\nSample data:")
        print(df_clean.head())
        
    except FileNotFoundError:
        print(f"Error: File not found: {input_path}")
        print("\nTo use this script:")
        print("1. Download CIQUAL data from https://ciqual.anses.fr/")
        print("2. Save it as data/ciqual.xlsx")
        print("3. Run this script again")
        
        # Create a sample CSV for development
        print("\nCreating sample CSV for development...")
        create_sample_csv(output_path)
    
    except Exception as e:
        print(f"Error processing CIQUAL data: {e}")
        print("\nCreating sample CSV for development...")
        create_sample_csv(output_path)


def create_sample_csv(output_path: str = "data/ciqual_clean.csv") -> None:
    """
    Create a sample CSV with common foods for development/testing.
    
    Args:
        output_path: Path to output CSV file
    """
    sample_data = {
        'food_code': [
            '36000', '9100', '20047', '13001', '9003',
            '26036', '22000', '4020', '15076', '19000',
            '17270', '20041', '6200', '9110', '13034'
        ],
        'food_name': [
            'Chicken breast, raw',
            'Brown rice, cooked',
            'Broccoli, raw',
            'Banana',
            'Oats, raw',
            'Salmon, raw',
            'Eggs, whole, raw',
            'Sweet potato, raw',
            'Almonds',
            'Greek yogurt, plain',
            'Olive oil',
            'Spinach, raw',
            'Beef, ground, 90% lean',
            'Quinoa, cooked',
            'Avocado',
        ],
        'category': [
            'Meat', 'Grains', 'Vegetables', 'Fruits', 'Grains',
            'Fish', 'Eggs', 'Vegetables', 'Nuts', 'Dairy',
            'Oils', 'Vegetables', 'Meat', 'Grains', 'Fruits'
        ],
        'kcal_100g': [
            120, 112, 34, 89, 389,
            208, 143, 86, 579, 59,
            884, 23, 176, 120, 160
        ],
        'protein_100g': [
            23.0, 2.6, 2.8, 1.1, 16.9,
            20.4, 12.6, 1.6, 21.2, 10.0,
            0.0, 2.9, 19.4, 4.4, 2.0
        ],
        'carbs_100g': [
            0.0, 23.5, 6.6, 22.8, 66.3,
            0.0, 1.1, 20.1, 21.6, 3.6,
            0.0, 3.6, 0.0, 21.3, 8.5
        ],
        'fat_100g': [
            2.6, 0.9, 0.4, 0.3, 6.9,
            13.4, 9.5, 0.1, 49.9, 0.4,
            100.0, 0.4, 10.0, 1.9, 14.7
        ],
        'fiber_100g': [
            0.0, 1.8, 2.6, 2.6, 10.6,
            0.0, 0.0, 3.0, 12.5, 0.0,
            0.0, 2.2, 0.0, 2.8, 6.7
        ],
        'sugars_100g': [
            0.0, 0.2, 1.7, 12.2, 0.0,
            0.0, 0.4, 4.2, 4.4, 3.6,
            0.0, 0.4, 0.0, 0.9, 0.7
        ],
    }
    
    df = pd.DataFrame(sample_data)
    
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    df.to_csv(output_path, index=False, encoding='utf-8')
    
    print(f"Sample CSV created: {output_path}")
    print(f"Rows: {len(df)}")


if __name__ == "__main__":
    preprocess_ciqual()
