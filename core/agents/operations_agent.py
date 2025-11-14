"""
Operations Agent
Specialized agent for operational data and time tracking analysis.
"""

from typing import Dict, Any, List
import logging
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class OperationsAgent(BaseAgent):
    """Agent specialized in operations and time tracking analysis."""

    def __init__(self, agent_id: str, llm_config: Dict[str, Any]):
        """Initialize Operations agent."""
        super().__init__(
            agent_id=agent_id,
            name="Operations Agent",
            llm_config=llm_config,
            memory_limit=20,
        )

        self.system_prompt = """
        You are an Operations Analysis Agent. Your role is to:
        - Analyze time tracking and project data
        - Identify productivity trends and patterns
        - Calculate project profitability and utilization rates
        - Flag over-budget or delayed projects
        - Provide resource allocation recommendations
        
        Always provide specific, actionable insights based on the data.
        """

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process operations data and generate insights.

        Args:
            input_data: Dictionary containing operations data
                - time_logs: List of time log records
                - projects: List of project records
                - query: Specific question or analysis request

        Returns:
            Dictionary with operations insights and recommendations
        """
        logger.info(f"{self.name} processing operations data")

        time_logs = input_data.get("time_logs", [])
        projects = input_data.get("projects", [])
        query = input_data.get("query", "Analyze operational efficiency")

        # Calculate metrics
        metrics = self._calculate_metrics(time_logs, projects)

        # Build context for LLM
        context = self._build_context(metrics, time_logs, projects)

        # Create prompt
        prompt = f"""
        Operations Data Summary:
        {context}
        
        Question: {query}
        
        Please provide:
        1. Key operational insights
        2. Productivity analysis
        3. Project status and risks
        4. Recommendations for improvement
        """

        # Call LLM
        response = self.call_llm(prompt, self.system_prompt)

        return {
            "agent": self.name,
            "query": query,
            "insights": response,
            "metrics": metrics,
            "data_summary": {
                "total_time_logs": len(time_logs),
                "total_projects": len(projects),
            },
        }

    def _calculate_metrics(
        self, time_logs: List[Dict], projects: List[Dict]
    ) -> Dict[str, Any]:
        """Calculate operational metrics."""
        metrics = {}

        # Time log metrics
        if time_logs:
            total_hours = sum(log.get("duration_hours", 0) for log in time_logs)
            total_cost = sum(log.get("total_cost", 0) for log in time_logs)
            billable_hours = sum(
                log.get("duration_hours", 0)
                for log in time_logs
                if log.get("is_billable")
            )

            metrics["total_hours"] = total_hours
            metrics["total_cost"] = total_cost
            metrics["billable_hours"] = billable_hours

            if total_hours > 0:
                metrics["utilization_rate"] = (billable_hours / total_hours) * 100

            # Hours by project
            hours_by_project = {}
            for log in time_logs:
                project = log.get("project_name", "Unknown")
                hours_by_project[project] = hours_by_project.get(project, 0) + log.get(
                    "duration_hours", 0
                )
            metrics["hours_by_project"] = hours_by_project

            # Hours by user
            hours_by_user = {}
            for log in time_logs:
                user = log.get("user_name", "Unknown")
                hours_by_user[user] = hours_by_user.get(user, 0) + log.get(
                    "duration_hours", 0
                )
            metrics["hours_by_user"] = hours_by_user

        # Project metrics
        if projects:
            active_projects = [p for p in projects if p.get("status") == "active"]
            completed_projects = [p for p in projects if p.get("status") == "completed"]

            metrics["active_projects_count"] = len(active_projects)
            metrics["completed_projects_count"] = len(completed_projects)

            total_budget = sum(p.get("budget", 0) for p in projects)
            total_spent = sum(p.get("total_cost", 0) for p in projects)

            metrics["total_budget"] = total_budget
            metrics["total_spent"] = total_spent

            if total_budget > 0:
                metrics["budget_utilization"] = (total_spent / total_budget) * 100

        return metrics

    def _build_context(
        self, metrics: Dict[str, Any], time_logs: List[Dict], projects: List[Dict]
    ) -> str:
        """Build context summary from operations data."""
        context_parts = []

        # Time metrics
        context_parts.append("Time Tracking Summary:")
        context_parts.append(f"  Total Hours: {metrics.get('total_hours', 0):.1f}")
        context_parts.append(
            f"  Billable Hours: {metrics.get('billable_hours', 0):.1f}"
        )

        if "utilization_rate" in metrics:
            context_parts.append(
                f"  Utilization Rate: {metrics['utilization_rate']:.1f}%"
            )

        # Project metrics
        if "active_projects_count" in metrics:
            context_parts.append(
                f"\nActive Projects: {metrics['active_projects_count']}"
            )
            context_parts.append(
                f"Completed Projects: {metrics['completed_projects_count']}"
            )

        if "total_budget" in metrics:
            context_parts.append(f"Total Budget: ${metrics['total_budget']:,.2f}")
            context_parts.append(f"Total Spent: ${metrics['total_spent']:,.2f}")

            if "budget_utilization" in metrics:
                context_parts.append(
                    f"Budget Utilization: {metrics['budget_utilization']:.1f}%"
                )

        return "\n".join(context_parts)

    def identify_over_budget_projects(self, projects: List[Dict]) -> List[Dict]:
        """
        Identify projects that are over budget.

        Args:
            projects: List of project records

        Returns:
            List of over-budget projects
        """
        over_budget = []

        for project in projects:
            budget = project.get("budget", 0)
            spent = project.get("total_cost", 0)

            if budget > 0 and spent > budget:
                over_budget.append(
                    {
                        "project": project.get("project_name"),
                        "budget": budget,
                        "spent": spent,
                        "overage": spent - budget,
                        "overage_percent": ((spent - budget) / budget) * 100,
                    }
                )

        return over_budget
