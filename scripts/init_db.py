"""
Database initialization script.
Creates all tables in the database.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.database.connection import init_db
from core.database.models_crm import CRMDeal, CRMContact, CRMActivity
from core.database.models_finance import FinanceInvoice, FinancePayment, FinanceCustomer
from core.database.models_marketing import MarketingCampaign, MarketingAdCreative
from core.database.models_operations import OperationsTimeLog, OperationsProject
from core.utils.config import config
from core.utils.logging_config import setup_logging
import logging

# Setup logging
setup_logging(log_level=config.get("logging.level", "INFO"))
logger = logging.getLogger(__name__)


def main():
    """Initialize the database and create all tables."""
    try:
        logger.info("Initializing database...")

        # Get database URL from config
        database_url = config.get("database.url")

        if not database_url:
            logger.error("DATABASE_URL not configured. Please set it in .env file.")
            sys.exit(1)

        # Initialize database
        db_manager = init_db(
            database_url=database_url, echo=config.get("database.echo", False)
        )

        # Create all tables
        db_manager.create_tables()

        logger.info("Database initialized successfully!")
        logger.info("All tables created.")

    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
