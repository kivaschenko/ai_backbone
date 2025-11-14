"""
Base connector class for all data integrations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BaseConnector(ABC):
    """Abstract base class for all external data connectors."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize connector with configuration.

        Args:
            config: Configuration dictionary with credentials and settings
        """
        self.config = config
        self.last_sync = None

    @abstractmethod
    def authenticate(self) -> bool:
        """
        Authenticate with the external service.

        Returns:
            bool: True if authentication successful
        """
        pass

    @abstractmethod
    def fetch_data(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Fetch data from the external service.

        Returns:
            List of data records
        """
        pass

    @abstractmethod
    def normalize_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normalize raw data to unified schema.

        Args:
            raw_data: Raw data from external service

        Returns:
            Normalized data records
        """
        pass

    def validate_data(self, data: List[Dict[str, Any]]) -> bool:
        """
        Validate data integrity.

        Args:
            data: Data to validate

        Returns:
            bool: True if validation passes
        """
        if not data:
            logger.warning("Empty data received")
            return False
        return True

    def sync(self) -> List[Dict[str, Any]]:
        """
        Complete sync process: authenticate, fetch, normalize, validate.

        Returns:
            Normalized and validated data
        """
        try:
            if not self.authenticate():
                raise Exception("Authentication failed")

            raw_data = self.fetch_data()
            normalized_data = self.normalize_data(raw_data)

            if self.validate_data(normalized_data):
                self.last_sync = datetime.utcnow()
                logger.info(f"Sync completed: {len(normalized_data)} records")
                return normalized_data
            else:
                raise Exception("Data validation failed")

        except Exception as e:
            logger.error(f"Sync failed: {str(e)}")
            raise
