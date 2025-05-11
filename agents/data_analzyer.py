import pandas as pd
from typing import Dict, Any
import logging

class DataAnalyzerAgent:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_sales_summary(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Generate comprehensive sales summary statistics"""
        try:
            return {
                'total_sales': f"{data['Quantity'].sum():,} units",
                'average_price': f"${data['Price'].mean():,.2f}",
                'top_make_model': self._get_top_make_model(data),
                'top_region': data.groupby('Region', observed=True)['Quantity'].sum().idxmax(),
                'yearly_growth': self._calculate_yearly_growth(data),
                'price_distribution': {
                    'min': f"${data['Price'].min():,.2f}",
                    'max': f"${data['Price'].max():,.2f}",
                    'median': f"${data['Price'].median():,.2f}"
                }
            }
        except Exception as e:
            self.logger.error(f"Summary generation failed: {str(e)}")
            return {'error': str(e)}

    def get_yearly_trends(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate yearly sales trends with breakdowns"""
        try:
            data['Year'] = pd.to_datetime(data['Year'].astype(str))  # Fixed missing parenthesis
            yearly = data.groupby('Year', observed=True)['Quantity'].sum()
            
            return {
                'total_by_year': yearly.to_dict(),
                'by_make': {
                    make: data[data['Make'] == make]
                        .groupby('Year', observed=True)['Quantity'].sum().to_dict()
                    for make in data['Make'].unique()
                },
                'by_region': data.groupby(['Year', 'Region'], observed=True)['Quantity']
                                .sum().unstack().to_dict(),
                'growth_rate': self._calculate_growth_rate(yearly)
            }
        except Exception as e:
            self.logger.error(f"Trend analysis failed: {str(e)}")
            return {'error': str(e)}

    def _calculate_yearly_growth(self, data: pd.DataFrame) -> float:
        """Calculate yearly growth rate"""
        try:
            yearly_sales = data.groupby('Year', observed=True)['Quantity'].sum()
            return yearly_sales.pct_change().mean()
        except Exception as e:
            self.logger.error(f"Yearly growth calculation failed: {str(e)}")
            return 0.0

    def _calculate_growth_rate(self, yearly_sales: pd.Series) -> float:
        """Calculate average annual growth rate"""
        try:
            return yearly_sales.pct_change().mean()
        except Exception as e:
            self.logger.error(f"Growth rate calculation failed: {str(e)}")
            return 0.0

    def _get_top_make_model(self, data: pd.DataFrame) -> str:
        """Identify top selling make and model combination"""
        try:
            if data.empty:
                return "No data available"
                
            clean_data = data.dropna(subset=['Make', 'Model', 'Quantity'])
            if clean_data.empty:
                return "No valid data available"
                
            grouped = clean_data.groupby(['Make', 'Model'], observed=True)['Quantity'].sum()
            if grouped.empty:
                return "No sales data available"
                
            top_combo = grouped.idxmax()
            return f"{top_combo[0]} {top_combo[1]}"
        except Exception as e:
            self.logger.error(f"Failed to identify top make/model: {str(e)}")
            return "Unknown"