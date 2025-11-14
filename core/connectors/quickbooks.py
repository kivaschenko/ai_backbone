"""
QuickBooks Connector
Handles authentication and data fetching from QuickBooks Online API.
"""

from typing import Dict, Any, List, Optional
import requests
import logging
from .base import BaseConnector

logger = logging.getLogger(__name__)


class QuickBooksConnector(BaseConnector):
    """Connector for QuickBooks Online API integration."""

    BASE_URL = "https://quickbooks.api.intuit.com/v3/company"

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize QuickBooks connector.

        Args:
            config: Must include client_id, client_secret, refresh_token, realm_id
        """
        super().__init__(config)
        self.access_token = None
        self.realm_id = config.get("realm_id")

    def authenticate(self) -> bool:
        """
        Authenticate using OAuth 2.0.

        Returns:
            bool: True if authentication successful
        """
        try:
            auth_url = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
            }
            data = {
                "grant_type": "refresh_token",
                "refresh_token": self.config["refresh_token"],
            }

            response = requests.post(
                auth_url,
                headers=headers,
                data=data,
                auth=(self.config["client_id"], self.config["client_secret"]),
            )
            response.raise_for_status()

            self.access_token = response.json()["access_token"]
            logger.info("QuickBooks authentication successful")
            return True

        except Exception as e:
            logger.error(f"QuickBooks authentication failed: {str(e)}")
            return False

    def fetch_data(self, entity: str = "Invoice", **kwargs) -> List[Dict[str, Any]]:
        """
        Fetch data from QuickBooks.

        Args:
            entity: Entity type (Invoice, Customer, Payment, etc.)
            **kwargs: Additional query parameters

        Returns:
            List of records from QuickBooks
        """
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
        }

        # Build query
        query = kwargs.get("query", f"SELECT * FROM {entity}")
        url = f"{self.BASE_URL}/{self.realm_id}/query"

        params = {"query": query, "minorversion": "65"}

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        data = response.json()
        records = data.get("QueryResponse", {}).get(entity, [])

        logger.info(f"Fetched {len(records)} {entity} records from QuickBooks")
        return records

    def normalize_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normalize QuickBooks data to unified schema.

        Args:
            raw_data: Raw data from QuickBooks

        Returns:
            Normalized data records
        """
        normalized = []

        for record in raw_data:
            normalized.append(
                {
                    "id": record.get("Id"),
                    "source": "quickbooks",
                    "doc_number": record.get("DocNumber"),
                    "amount": record.get("TotalAmt") or record.get("Balance"),
                    "customer_ref": record.get("CustomerRef", {}).get("value"),
                    "customer_name": record.get("CustomerRef", {}).get("name"),
                    "txn_date": record.get("TxnDate"),
                    "due_date": record.get("DueDate"),
                    "created_time": record.get("MetaData", {}).get("CreateTime"),
                    "modified_time": record.get("MetaData", {}).get("LastUpdatedTime"),
                    "raw_data": record,
                }
            )

        return normalized
