"""
Marketing Agent
Specialized agent for marketing and ad campaign analysis.
"""

from typing import Dict, Any, List
import logging
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class MarketingAgent(BaseAgent):
    """Agent specialized in marketing and advertising analysis."""

    def __init__(self, agent_id: str, llm_config: Dict[str, Any]):
        """Initialize Marketing agent."""
        super().__init__(
            agent_id=agent_id,
            name="Marketing Agent",
            llm_config=llm_config,
            memory_limit=20,
        )

        self.system_prompt = """
        You are a Marketing Analysis Agent. Your role is to:
        - Analyze ad campaign performance across platforms
        - Calculate and interpret marketing metrics (CTR, CPC, ROAS, etc.)
        - Identify high and low performing campaigns
        - Provide budget optimization recommendations
        - Suggest A/B testing opportunities
        
        Always provide specific, data-driven recommendations with numbers.
        """

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process marketing data and generate insights.

        Args:
            input_data: Dictionary containing marketing data
                - campaigns: List of campaign records
                - query: Specific question or analysis request

        Returns:
            Dictionary with marketing insights and recommendations
        """
        logger.info(f"{self.name} processing marketing data")

        campaigns = input_data.get("campaigns", [])
        query = input_data.get("query", "Analyze campaign performance")

        # Calculate aggregate metrics
        metrics = self._calculate_aggregate_metrics(campaigns)

        # Build context for LLM
        context = self._build_context(metrics, campaigns)

        # Create prompt
        prompt = f"""
        Marketing Data Summary:
        {context}
        
        Question: {query}
        
        Please provide:
        1. Campaign performance insights
        2. High and low performers
        3. Budget optimization recommendations
        4. Testing opportunities
        """

        # Call LLM
        response = self.call_llm(prompt, self.system_prompt)

        return {
            "agent": self.name,
            "query": query,
            "insights": response,
            "metrics": metrics,
            "data_summary": {"total_campaigns": len(campaigns)},
        }

    def _calculate_aggregate_metrics(self, campaigns: List[Dict]) -> Dict[str, Any]:
        """Calculate aggregate marketing metrics."""
        metrics = {
            "total_spend": 0,
            "total_impressions": 0,
            "total_clicks": 0,
            "total_conversions": 0,
            "total_conversion_value": 0,
        }

        for campaign in campaigns:
            metrics["total_spend"] += campaign.get("spend", 0)
            metrics["total_impressions"] += campaign.get("impressions", 0)
            metrics["total_clicks"] += campaign.get("clicks", 0)
            metrics["total_conversions"] += campaign.get("conversions", 0)
            metrics["total_conversion_value"] += campaign.get("conversion_value", 0)

        # Calculate derived metrics
        if metrics["total_impressions"] > 0:
            metrics["avg_ctr"] = (
                metrics["total_clicks"] / metrics["total_impressions"]
            ) * 100

        if metrics["total_clicks"] > 0:
            metrics["avg_cpc"] = metrics["total_spend"] / metrics["total_clicks"]

        if metrics["total_conversions"] > 0:
            metrics["avg_cpa"] = metrics["total_spend"] / metrics["total_conversions"]

        if metrics["total_spend"] > 0:
            metrics["roas"] = metrics["total_conversion_value"] / metrics["total_spend"]

        return metrics

    def _build_context(self, metrics: Dict[str, Any], campaigns: List[Dict]) -> str:
        """Build context summary from marketing data."""
        context_parts = []

        # Overall metrics
        context_parts.append("Overall Performance:")
        context_parts.append(f"  Total Spend: ${metrics.get('total_spend', 0):,.2f}")
        context_parts.append(
            f"  Total Impressions: {metrics.get('total_impressions', 0):,}"
        )
        context_parts.append(f"  Total Clicks: {metrics.get('total_clicks', 0):,}")
        context_parts.append(
            f"  Total Conversions: {metrics.get('total_conversions', 0)}"
        )

        if "avg_ctr" in metrics:
            context_parts.append(f"  Average CTR: {metrics['avg_ctr']:.2f}%")
        if "avg_cpc" in metrics:
            context_parts.append(f"  Average CPC: ${metrics['avg_cpc']:.2f}")
        if "avg_cpa" in metrics:
            context_parts.append(f"  Average CPA: ${metrics['avg_cpa']:.2f}")
        if "roas" in metrics:
            context_parts.append(f"  ROAS: {metrics['roas']:.2f}x")

        # Campaign breakdown by source
        if campaigns:
            sources = {}
            for campaign in campaigns:
                source = campaign.get("source", "Unknown")
                sources[source] = sources.get(source, 0) + 1
            context_parts.append(f"\nCampaigns by Platform: {sources}")

        return "\n".join(context_parts)

    def identify_top_campaigns(
        self, campaigns: List[Dict], metric: str = "roas", top_n: int = 5
    ) -> List[Dict]:
        """
        Identify top performing campaigns.

        Args:
            campaigns: List of campaign records
            metric: Metric to sort by (roas, ctr, conversions, etc.)
            top_n: Number of top campaigns to return

        Returns:
            List of top performing campaigns
        """
        # Sort campaigns by specified metric
        sorted_campaigns = sorted(
            campaigns, key=lambda c: c.get(metric, 0), reverse=True
        )

        return sorted_campaigns[:top_n]

    def identify_underperforming_campaigns(
        self, campaigns: List[Dict], metric: str = "roas", threshold: float = 1.0
    ) -> List[Dict]:
        """
        Identify underperforming campaigns.

        Args:
            campaigns: List of campaign records
            metric: Metric to evaluate
            threshold: Minimum acceptable value

        Returns:
            List of underperforming campaigns
        """
        underperforming = []

        for campaign in campaigns:
            value = campaign.get(metric, 0)
            if value < threshold:
                underperforming.append(
                    {
                        "campaign": campaign,
                        "metric": metric,
                        "value": value,
                        "threshold": threshold,
                    }
                )

        return underperforming
