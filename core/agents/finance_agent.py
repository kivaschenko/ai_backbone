"""
Finance Agent
Specialized agent for financial data analysis and insights.
"""

from typing import Dict, Any, List
import logging
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class FinanceAgent(BaseAgent):
    """Agent specialized in financial data analysis."""

    def __init__(self, agent_id: str, llm_config: Dict[str, Any]):
        """Initialize Finance agent."""
        super().__init__(
            agent_id=agent_id,
            name="Finance Agent",
            llm_config=llm_config,
            memory_limit=20,
        )

        self.system_prompt = """
        You are a Financial Analysis Agent. Your role is to:
        - Analyze invoices, payments, and revenue data
        - Identify cash flow trends and patterns
        - Calculate key financial metrics (AR aging, DSO, etc.)
        - Flag overdue invoices and payment issues
        - Provide financial forecasts and recommendations
        
        Always provide specific, data-driven insights with numbers.
        """

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process financial data and generate insights.

        Args:
            input_data: Dictionary containing financial data
                - invoices: List of invoice records
                - payments: List of payment records
                - customers: List of customer records
                - query: Specific question or analysis request

        Returns:
            Dictionary with financial insights and recommendations
        """
        logger.info(f"{self.name} processing financial data")

        invoices = input_data.get("invoices", [])
        payments = input_data.get("payments", [])
        customers = input_data.get("customers", [])
        query = input_data.get("query", "Analyze current financial status")

        # Calculate metrics
        metrics = self._calculate_metrics(invoices, payments, customers)

        # Build context for LLM
        context = self._build_context(metrics, invoices, payments)

        # Create prompt
        prompt = f"""
        Financial Data Summary:
        {context}
        
        Question: {query}
        
        Please provide:
        1. Key financial insights
        2. Cash flow analysis
        3. Recommendations for improvement
        4. Any concerns or risks
        """

        # Call LLM
        response = self.call_llm(prompt, self.system_prompt)

        return {
            "agent": self.name,
            "query": query,
            "insights": response,
            "metrics": metrics,
            "data_summary": {
                "total_invoices": len(invoices),
                "total_payments": len(payments),
                "total_customers": len(customers),
            },
        }

    def _calculate_metrics(
        self, invoices: List[Dict], payments: List[Dict], customers: List[Dict]
    ) -> Dict[str, Any]:
        """Calculate key financial metrics."""
        metrics = {}

        # Invoice metrics
        if invoices:
            total_invoiced = sum(inv.get("total_amount", 0) for inv in invoices)
            total_outstanding = sum(inv.get("balance", 0) for inv in invoices)
            paid_invoices = [inv for inv in invoices if inv.get("status") == "paid"]
            overdue_invoices = [
                inv for inv in invoices if inv.get("status") == "unpaid"
            ]

            metrics["total_invoiced"] = total_invoiced
            metrics["total_outstanding"] = total_outstanding
            metrics["total_paid"] = total_invoiced - total_outstanding
            metrics["paid_count"] = len(paid_invoices)
            metrics["overdue_count"] = len(overdue_invoices)

        # Payment metrics
        if payments:
            total_received = sum(pay.get("amount", 0) for pay in payments)
            metrics["total_received"] = total_received

        # Customer metrics
        if customers:
            total_customer_balance = sum(cust.get("balance", 0) for cust in customers)
            metrics["total_ar"] = total_customer_balance
            metrics["active_customers"] = len([c for c in customers if c.get("active")])

        return metrics

    def _build_context(
        self, metrics: Dict[str, Any], invoices: List[Dict], payments: List[Dict]
    ) -> str:
        """Build context summary from financial data."""
        context_parts = []

        # Metrics summary
        if metrics:
            context_parts.append("Financial Metrics:")
            for key, value in metrics.items():
                if isinstance(value, (int, float)):
                    if "total" in key or "balance" in key or "ar" in key:
                        context_parts.append(f"  {key}: ${value:,.2f}")
                    else:
                        context_parts.append(f"  {key}: {value}")

        # Invoice status breakdown
        if invoices:
            statuses = {}
            for inv in invoices:
                status = inv.get("status", "Unknown")
                statuses[status] = statuses.get(status, 0) + 1
            context_parts.append(f"\nInvoice Status: {statuses}")

        return "\n".join(context_parts)

    def identify_overdue_invoices(
        self, invoices: List[Dict], days_threshold: int = 30
    ) -> List[Dict]:
        """
        Identify overdue invoices.

        Args:
            invoices: List of invoice records
            days_threshold: Days past due threshold

        Returns:
            List of overdue invoice details
        """
        overdue = []

        for invoice in invoices:
            if invoice.get("status") in ["unpaid", "partial"]:
                # Calculate days overdue
                # Add logic to check due_date vs current date

                overdue.append(
                    {
                        "invoice_id": invoice.get("source_id"),
                        "customer": invoice.get("customer_name"),
                        "amount": invoice.get("balance"),
                        "due_date": invoice.get("due_date"),
                    }
                )

        return overdue
