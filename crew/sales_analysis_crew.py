import os
import pandas as pd
from typing import Dict, Any, Optional
from crewai import Crew, Process
import logging
from agents.data_loader import DataLoaderAgent
from agents.data_analzyer import DataAnalyzerAgent
from agents.query_finder import QueryHandlerAgent
from tasks.analysis_tasks import AnalysisTasks

logger = logging.getLogger(__name__)

class SalesAnalysisCrew:
    def __init__(self, file_path: str, verbose: bool = True):
        self.file_path = os.path.abspath(file_path)
        self.verbose = verbose
        self._validate_data_file()
        self.data_loader = DataLoaderAgent()
        self.analyzer = DataAnalyzerAgent()
        self.query_handler = QueryHandlerAgent(use_llm=True)
        self.tasks = AnalysisTasks()
        if self.verbose:
            logger.info(f"Initialized with data: {self.file_path}")

    def _validate_data_file(self):
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Data file not found: {self.file_path}")
        if not self.file_path.endswith('.csv'):
            logger.warning("File extension is not .csv - may cause parsing issues")

    def run(self, query: Optional[str] = None) -> Dict[str, Any]:
        try:
            data = self._load_data()
            analysis = {
                'summary': self.analyzer.get_sales_summary(data),
                'trends': self.analyzer.get_yearly_trends(data),
                'metadata': {
                    'years_covered': f"{data['Year'].min()} to {data['Year'].max()}",
                    'unique_models': data['Model'].nunique()
                }
            }
            if query:
                analysis['query_response'] = self._process_query(data, query)
            return analysis
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}", exc_info=True)
            return {'error': str(e)}

    def _load_data(self) -> pd.DataFrame:
        data = self.data_loader.load_data(self.file_path)
        required_cols = {'Year', 'Make', 'Model', 'Quantity', 'Price'}
        if not required_cols.issubset(data.columns):
            missing = required_cols - set(data.columns)
            raise ValueError(f"Missing columns: {missing}")
        data['Date'] = pd.to_datetime(data['Year'].astype(str) + '-01-01')
        return data

    def _process_query(self, data: pd.DataFrame, query: str) -> str:
        """Handle all types of user queries with appropriate routing"""
        query_lower = query.lower()
        
        # Structured data responses
        if any(kw in query_lower for kw in ['projection', 'forecast', 'predict']):
            return self._handle_projection_query(data)
        elif any(kw in query_lower for kw in ['compare', 'vs', 'versus']):
            return self._handle_comparison_query(data, query)
        elif any(kw in query_lower for kw in ['top', 'best', 'worst', 'ranking']):
            return self._handle_ranking_query(data, query)
        else:
            return self._handle_general_query(data, query)

    def _handle_projection_query(self, data: pd.DataFrame) -> str:
        """Force direct LLM call for projections"""
        return self.query_handler.execute_task(
            f"Generate sales projections based on: {data.head().to_dict()}\n"
            "Format response as:\n"
            "📈 3-Year Projection\n"
            "------------------------\n"
            "[content]"
        )
    
    # def _handle_projection_query(self, data: pd.DataFrame) -> str:
    #     """Generate sales projections based on historical trends"""
    #     trends = self.analyzer.get_yearly_trends(data)
    #     if 'error' in trends:
    #         return trends['error']
        
    #     growth_rate = trends.get('growth_rate', 0)
    #     last_year = max(trends['total_by_year'].keys())
    #     last_quantity = trends['total_by_year'][last_year]
        
    #     projections = []
    #     for years_ahead in range(1, 4):
    #         year = last_year.year + years_ahead
    #         projected = int(last_quantity * (1 + growth_rate) ** years_ahead)
    #         projections.append(f"{year}: {projected:,} units")
        
    #     return (
    #         "📈 3-Year Sales Projection\n"
    #         "------------------------\n"
    #         f"Based on historical growth rate: {growth_rate:.1%}\n"
    #         "Projected annual sales:\n"
    #         + "\n".join(f"- {p}" for p in projections)
    #     )

    def _handle_comparison_query(self, data: pd.DataFrame, query: str) -> str:
        """Compare makes/models/regions"""
        try:
            # Extract comparison targets from query
            targets = []
            for make in data['Make'].unique():
                if make.lower() in query.lower():
                    targets.append(make)
            
            if len(targets) < 2:
                return "Could not identify two models/makes to compare"
            
            # Generate comparison data
            comparison = {}
            for target in targets:
                target_data = data[data['Make'].str.lower() == target.lower()]
                comparison[target] = {
                    'total_sales': target_data['Quantity'].sum(),
                    'avg_price': target_data['Price'].mean()
                }
            
            # Format response
            lines = [f"🔍 Comparison: {' vs '.join(targets)}"]
            for target, stats in comparison.items():
                lines.append(
                    f"- {target}: {stats['total_sales']:,} units sold, "
                    f"${stats['avg_price']:,.2f} avg price"
                )
            return "\n".join(lines)
            
        except Exception as e:
            logger.error(f"Comparison failed: {str(e)}")
            return f"Could not complete comparison: {str(e)}"

    def _handle_ranking_query(self, data: pd.DataFrame, query: str) -> str:
        """Handle top/best/worst ranking requests"""
        try:
            n = 3  # Default number of results
            if "top" in query.lower():
                # Extract number if present (e.g., "top 5")
                words = query.lower().split()
                if len(words) > words.index("top") + 1 and words[words.index("top") + 1].isdigit():
                    n = int(words[words.index("top") + 1])
            
            by = "Quantity"  # Default metric
            if "expensive" in query.lower():
                by = "Price"
            elif "revenue" in query.lower():
                data['Revenue'] = data['Quantity'] * data['Price']
                by = "Revenue"
            
            ascending = "worst" in query.lower()
            results = (
                data.groupby(['Make', 'Model'], observed=True)
                [by].sum()
                .sort_values(ascending=ascending)
                .head(n)
            )
            
            title = "🏆 Top" if not ascending else "⚠️ Worst"
            lines = [f"{title} {n} by {by}:"]
            for (make, model), value in results.items():
                if by == "Price":
                    lines.append(f"- {make} {model}: ${value:,.2f}")
                else:
                    lines.append(f"- {make} {model}: {value:,} units")
            
            return "\n".join(lines)
            
        except Exception as e:
            logger.error(f"Ranking failed: {str(e)}")
            return f"Could not generate rankings: {str(e)}"

    def _handle_general_query(self, data: pd.DataFrame, query: str) -> str:
        """Fallback handler for all other queries using LLM"""
        try:
            # First try to answer from structured data
            summary = self.analyzer.get_sales_summary(data)
            if "growth" in query.lower() and 'yearly_growth' in summary:
                return f"Average yearly growth: {float(summary['yearly_growth']):.1%}"
            
            # Fall back to LLM
            context = {
                'summary': summary,
                'trends': self.analyzer.get_yearly_trends(data),
                'sample_data': data.head(3).to_dict('records')
            }
            return self.query_handler.agent.execute_task(
                f"Answer this car sales question: {query}\n\nContext: {context}"
            )
            
        except Exception as e:
            logger.error(f"Query handling failed: {str(e)}")
            return "Could not process this query"