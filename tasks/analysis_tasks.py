from crewai import Task
from typing import Dict, Any

class AnalysisTasks:
    def __init__(self):
        self.task_config = {
            'verbose': True,
            'async_execution': False
        }

    def create_summary_task(self, agent, data: Dict[str, Any]) -> Task:
        return Task(
            description="""Generate comprehensive sales summary statistics including:
            - Total units sold
            - Average price
            - Top performing makes/models
            - Regional performance
            - Price distribution""",
            agent=agent,
            expected_output="Complete sales summary in dictionary format",
            **self.task_config
        )

    def create_trends_task(self, agent, data: Dict[str, Any]) -> Task:
        return Task(
            description="""Analyze yearly sales trends including:
            - Year-over-year growth
            - Make-specific trends
            - Regional breakdowns
            - Identify seasonal patterns""",
            agent=agent,
            expected_output="Detailed trends analysis in dictionary format",
            **self.task_config
        )

    def create_query_task(self, agent, context: Dict[str, Any], query: str) -> Task:
        return Task(
            description=f"""Analyze the car sales data and answer the query: {query}
            
            Context Data:
            - Historical Trends: {context.get('trends', {})}
            - Current Summary: {context.get('summary', {})}
            - Sample Records: {context.get('sample', [])[:2]}""",
            agent=agent,
            expected_output="A detailed, data-backed answer to the query",
            **self.task_config
        )

    def create_projection_task(self, agent, trends: Dict[str, Any]) -> Task:
        return Task(
            description=f"""Generate a detailed 3-year sales projection based on:
            - Historical growth rate: {trends.get('growth_rate', 0):.1%}
            - Current trends: {trends.get('total_by_year', {})}
            
            Include:
            1. Total projected sales by year
            2. Breakdown by make/model
            3. Regional projections""",
            agent=agent,
            expected_output="Formatted markdown report with clear projections",
            async_execution=False
        )

    def create_comparison_task(self, agent, data: Dict[str, Any]) -> Task:
        return Task(
            description="""Compare performance across:
            - Different makes/models
            - Regions
            - Price segments""",
            agent=agent,
            expected_output="Comparative analysis report",
            **self.task_config
        )