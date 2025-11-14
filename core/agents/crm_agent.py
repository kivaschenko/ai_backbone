"""
CRM Agent
Specialized agent for CRM data analysis and insights.
"""

from typing import Dict, Any, List
import logging
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class CRMAgent(BaseAgent):
    """Agent specialized in CRM data analysis."""

    def __init__(self, agent_id: str, llm_config: Dict[str, Any]):
        """Initialize CRM agent."""
        super().__init__(
            agent_id=agent_id, name="CRM Agent", llm_config=llm_config, memory_limit=20
        )

        self.system_prompt = """
        You are a CRM Analysis Agent. Your role is to:
        - Analyze deals, contacts, and sales activities
        - Identify trends and patterns in the sales pipeline
        - Provide insights on deal velocity and win rates
        - Suggest actions to improve sales outcomes
        - Flag at-risk deals that need attention
        
        Always provide specific, actionable insights based on the data.
        """

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process CRM data and generate insights.

        Args:
            input_data: Dictionary containing CRM data
                - deals: List of deal records
                - contacts: List of contact records
                - activities: List of activity records
                - query: Specific question or analysis request

        Returns:
            Dictionary with insights and recommendations
        """
        logger.info(f"{self.name} processing CRM data")

        deals = input_data.get("deals", [])
        contacts = input_data.get("contacts", [])
        activities = input_data.get("activities", [])
        query = input_data.get("query", "Analyze the current sales pipeline")

        # Build context for LLM
        context = self._build_context(deals, contacts, activities)

        # Create prompt
        prompt = f"""
        CRM Data Summary:
        {context}
        
        Question: {query}
        
        Please provide:
        1. Key insights from the data
        2. Specific recommendations
        3. Any risks or concerns
        """

        # Call LLM
        response = self.call_llm(prompt, self.system_prompt)

        return {
            "agent": self.name,
            "query": query,
            "insights": response,
            "data_summary": {
                "total_deals": len(deals),
                "total_contacts": len(contacts),
                "total_activities": len(activities),
            },
        }

    def _build_context(
        self, deals: List[Dict], contacts: List[Dict], activities: List[Dict]
    ) -> str:
        """Build context summary from CRM data."""
        context_parts = []

        # Deal summary
        if deals:
            total_value = sum(d.get("amount", 0) for d in deals)
            stages = {}
            for deal in deals:
                stage = deal.get("stage", "Unknown")
                stages[stage] = stages.get(stage, 0) + 1

            context_parts.append(
                f"Total Deals: {len(deals)}, Total Value: ${total_value:,.2f}"
            )
            context_parts.append(f"Deals by Stage: {stages}")

        # Contact summary
        if contacts:
            context_parts.append(f"Total Contacts: {len(contacts)}")

        # Activity summary
        if activities:
            activity_types = {}
            for activity in activities:
                act_type = activity.get("activity_type", "Unknown")
                activity_types[act_type] = activity_types.get(act_type, 0) + 1

            context_parts.append(f"Recent Activities: {activity_types}")

        return "\n".join(context_parts)

    def identify_at_risk_deals(self, deals: List[Dict]) -> List[Dict]:
        """
        Identify deals that might be at risk.

        Args:
            deals: List of deal records

        Returns:
            List of at-risk deals with reasons
        """
        at_risk = []

        for deal in deals:
            risk_factors = []

            # Check for stale deals (no activity in 30+ days)
            # Check for deals close to deadline with low probability
            # Add more risk detection logic

            if risk_factors:
                at_risk.append({"deal": deal, "risk_factors": risk_factors})

        return at_risk
