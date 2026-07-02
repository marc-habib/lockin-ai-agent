"""
CIQUAL data preprocessing script.

Converts the official CIQUAL Excel file into a clean CSV with only
the columns needed for the application.

Usage:
    python scripts/preprocess_ciqual.py

Input: data/ciqual.xlsx (download from https://ciqual.anses.fr/)
Output: data/ciqual_clean.csv
"""

import pandas as pd
from pathlib import Path


def preprocess_ciqual(
    input_path: str = "data/ciqual.xlsx",
    output_path: str = "data/ciqual_clean.csv"
) -> None:
    """
    Preprocess CIQUAL data.
    
    Args:
        input_path: Path to input Excel file
        output_path: Path to output CSV file
    """
    print(f"Reading CIQUAL data from {input_path}...")
    
    try:
        # Read the Excel file
        # CIQUAL typically has data in the first sheet
        df = pd.read_excel(input_path, sheet_name=0)
        
        print(f"Loaded {len(df)} rows")
        print(f"Columns: {list(df.columns)[:10]}...")  # Show first 10 columns
        
        # Map CIQUAL column names to our schema
        # Note: Actual column names may vary - adjust based on your CIQUAL version
        column_mapping = {
            'alim_nom_fr': 'food_name',
            'alim_grp_nom_fr': 'category',
            'Energie, Règlement UE N° 1169/2011 (kcal/100 g)': 'kcal_100g',
            'Protéines, N x facteur de Jones (g/100 g)': 'protein_100g',
            'Glucides (g/100 g)': 'carbs_100g',
            'Lipides (g/100 g)': 'fat_100g',
            'Fibres alimentaires (g/100 g)': 'fiber_100g',
            'Sucres (g/100 g)': 'sugars_100g',
        }
        
        # Try to find matching columns (case-insensitive, partial match)
        actual_mapping = {}
        for ciqual_col in df.columns:
            for expected_col, our_col in column_mapping.items():
                if expected_col.lower() in ciqual_col.lower():
                    actual_mapping[ciqual_col] = our_col
                    break
        
        if not actual_mapping:
            print("Warning: Could not auto-detect columns. Using fallback...")
            # Fallback: assume first columns are in order
            df_clean = pd.DataFrame({
                'food_name': df.iloc[:, 1] if len(df.columns) > 1 else df.iloc[:, 0],
                'category': df.iloc[:, 2] if len(df.columns) > 2 else '',
                'kcal_100g': df.iloc[:, 3] if len(df.columns) > 3 else 0,
                'protein_100g': df.iloc[:, 4] if len(df.columns) > 4 else 0,
                'carbs_100g': df.iloc[:, 5] if len(df.columns) > 5 else 0,
                'fat_100g': df.iloc[:, 6] if len(df.columns) > 6 else 0,
                'fiber_100g': df.iloc[:, 7] if len(df.columns) > 7 else 0,
                'sugars_100g': df.iloc[:, 8] if len(df.columns) > 8 else 0,
            })
        else:
            # Rename columns
            df_clean = df.rename(columns=actual_mapping)
            
            # Select only the columns we need
            required_cols = ['food_name', 'category', 'kcal_100g', 'protein_100g', 
                           'carbs_100g', 'fat_100g', 'fiber_100g', 'sugars_100g']
            
            # Keep only columns that exist
            available_cols = [col for col in required_cols if col in df_clean.columns]
            df_clean = df_clean[available_cols]
        
        # Clean the data
        df_clean = df_clean.dropna(subset=['food_name'])  # Remove rows without food name
        
        # Fill missing numeric values with 0
        numeric_cols = ['kcal_100g', 'protein_100g', 'carbs_100g', 'fat_100g', 
                       'fiber_100g', 'sugars_100g']
        for col in numeric_cols:
            if col in df_clean.columns:
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce').fillna(0)
        
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
