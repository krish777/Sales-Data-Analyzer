from crewai import Agent
import pandas as pd
from typing import Optional, Union
import warnings
from datetime import datetime

class DataLoaderAgent:
    def __init__(self):
        self.agent = Agent(
            role='Data Quality Engineer',  # More specific role
            goal='Ensure clean, validated automotive sales data loading',
            backstory=(
                "Data specialist with 8+ years experience in ETL pipelines "
                "and automotive industry data standards"
            ),
            allow_delegation=False,
            verbose=True,
            llm=None,  # Critical for pure data tasks
            max_iter=1,
            memory=False,
            function_calling=False# Disable unnecessary memory
        )
        warnings.filterwarnings('ignore', category=UserWarning)  # Cleaner output

    def load_data(self, file_path: str) -> Optional[pd.DataFrame]:
        """
        Robust CSV loader with validation
        Returns:
            pd.DataFrame: Loaded data or None if failed
        """
        try:
            data = pd.read_csv(
                file_path,
                parse_dates=['Year'],  # Auto datetime conversion
                dtype={
                    'Make': 'category',
                    'Model': 'category',
                    'Region': 'category'
                },
                thousands=',',  # Handles formatted numbers
                encoding='utf-8'
            )
            return self._validate_data(data)
        except Exception as e:
            print(f"⛔ Failed to load data: {str(e)}")
            return None

    def preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Comprehensive preprocessing pipeline
        Args:
            data: Raw DataFrame
        Returns:
            pd.DataFrame: Processed data
        """
        if data is None:
            return None
            
        return (
            data
            .pipe(self._convert_dtypes)
            .pipe(self._handle_missing)
            .pipe(self._add_derived_fields)
        )

    # Private methods for cleaner interface
    def _validate_data(self, df: pd.DataFrame) -> Union[pd.DataFrame, None]:
        """Ensure required columns exist"""
        required = ['Year', 'Make', 'Model', 'Quantity', 'Price']
        if not all(col in df.columns for col in required):
            print(f"Missing columns. Required: {required}")
            return None
        return df

    def _convert_dtypes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Optimize data types"""
        return df.assign(
            Year=lambda x: pd.to_datetime(x['Year']),
            Make=lambda x: x['Make'].astype('category'),
            Model=lambda x: x['Model'].astype('category')
        )

    def _handle_missing(self, df: pd.DataFrame) -> pd.DataFrame:
        """Smart missing value handling"""
        return df.fillna({
            'Quantity': 0,
            'Price': df['Price'].median()  # More robust than mean
        })

    def _add_derived_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add calculated columns"""
        return df.assign(
            Revenue=lambda x: x['Quantity'] * x['Price'],
            YearMonth=lambda x: x['Year'].dt.to_period('M')
        )