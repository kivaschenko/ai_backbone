"""
Example script showing how to use the AI agents.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.agents.crm_agent import CRMAgent
from core.agents.finance_agent import FinanceAgent
from core.agents.marketing_agent import MarketingAgent
from core.agents.operations_agent import OperationsAgent
from core.utils.config import config
from core.utils.logging_config import setup_logging
import logging

# Setup logging
setup_logging(log_level="INFO")
logger = logging.getLogger(__name__)


def example_crm_analysis():
    """Example of using CRM Agent."""
    logger.info("=== CRM Agent Example ===")

    # Initialize agent
    agent = CRMAgent(
        agent_id="crm_example",
        llm_config={
            "model": config.get("llm.model"),
            "api_key": config.get("llm.api_key"),
            "temperature": config.get("llm.temperature"),
        },
    )

    # Sample data
    sample_deals = [
        {"name": "Deal 1", "stage": "Proposal", "amount": 50000},
        {"name": "Deal 2", "stage": "Negotiation", "amount": 75000},
        {"name": "Deal 3", "stage": "Closed Won", "amount": 100000},
    ]

    # Analyze
    result = agent.process(
        {"deals": sample_deals, "query": "What is the current pipeline status?"}
    )

    logger.info(f"Result: {result}")


def example_finance_analysis():
    """Example of using Finance Agent."""
    logger.info("=== Finance Agent Example ===")

    agent = FinanceAgent(
        agent_id="finance_example",
        llm_config={
            "model": config.get("llm.model"),
            "api_key": config.get("llm.api_key"),
        },
    )

    sample_invoices = [
        {"doc_number": "INV-001", "total_amount": 5000, "status": "paid"},
        {
            "doc_number": "INV-002",
            "total_amount": 3000,
            "status": "unpaid",
            "balance": 3000,
        },
    ]

    result = agent.process(
        {"invoices": sample_invoices, "query": "What is the outstanding AR?"}
    )

    logger.info(f"Result: {result}")


def example_marketing_analysis():
    """Example of using Marketing Agent."""
    logger.info("=== Marketing Agent Example ===")

    agent = MarketingAgent(
        agent_id="marketing_example",
        llm_config={
            "model": config.get("llm.model"),
            "api_key": config.get("llm.api_key"),
        },
    )

    sample_campaigns = [
        {
            "campaign_name": "Summer Sale",
            "spend": 1000,
            "impressions": 50000,
            "clicks": 500,
            "conversions": 25,
            "conversion_value": 5000,
        }
    ]

    result = agent.process(
        {"campaigns": sample_campaigns, "query": "How are our campaigns performing?"}
    )

    logger.info(f"Result: {result}")


def main():
    """Run all examples."""
    try:
        example_crm_analysis()
        print("\n" + "=" * 50 + "\n")

        example_finance_analysis()
        print("\n" + "=" * 50 + "\n")

        example_marketing_analysis()

    except Exception as e:
        logger.error(f"Example failed: {str(e)}")


if __name__ == "__main__":
    main()
