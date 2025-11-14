"""
Zoho CRM Connector
Handles authentication and data fetching from Zoho CRM.
"""

from typing import Dict, Any, List, Optional
import requests
import logging
from .base import BaseConnector

logger = logging.getLogger(__name__)


class ZohoCRMConnector(BaseConnector):
    """Connector for Zoho CRM API integration."""

    BASE_URL = "https://www.zohoapis.com/crm/v3"

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Zoho CRM connector.

        Args:
            config: Must include client_id, client_secret, refresh_token
        """
        super().__init__(config)
        self.access_token = None

    def authenticate(self) -> bool:
        """
        Authenticate using OAuth 2.0 refresh token flow.

        Returns:
            bool: True if authentication successful
        """
        try:
            auth_url = "https://accounts.zoho.com/oauth/v2/token"
            params = {
                "refresh_token": self.config["refresh_token"],
                "client_id": self.config["client_id"],
                "client_secret": self.config["client_secret"],
                "grant_type": "refresh_token",
            }

            response = requests.post(auth_url, data=params)
            response.raise_for_status()

            self.access_token = response.json()["access_token"]
            logger.info("Zoho CRM authentication successful")
            return True

        except Exception as e:
            logger.error(f"Zoho CRM authentication failed: {str(e)}")
            return False

    def fetch_data(self, module: str = "Deals", **kwargs) -> List[Dict[str, Any]]:
        """
        Fetch data from specified Zoho CRM module.

        Args:
            module: CRM module name (Deals, Contacts, Accounts, etc.)
            **kwargs: Additional query parameters

        Returns:
            List of records from Zoho CRM
        """
        headers = {"Authorization": f"Zoho-oauthtoken {self.access_token}"}
        url = f"{self.BASE_URL}/{module}"

        all_records = []
        page = 1
        per_page = kwargs.get("per_page", 200)

        while True:
            params = {"page": page, "per_page": per_page}
            params.update(kwargs)

            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()

            data = response.json()
            records = data.get("data", [])

            if not records:
                break

            all_records.extend(records)

            if not data.get("info", {}).get("more_records"):
                break

            page += 1

        logger.info(f"Fetched {len(all_records)} records from {module}")
        return all_records

    def normalize_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normalize Zoho CRM data to unified schema.

        Args:
            raw_data: Raw data from Zoho CRM

        Returns:
            Normalized data records
        """
        normalized = []

        for record in raw_data:
            normalized.append(
                {
                    "id": record.get("id"),
                    "source": "zoho_crm",
                    "name": record.get("Deal_Name") or record.get("Full_Name"),
                    "stage": record.get("Stage"),
                    "amount": record.get("Amount"),
                    "owner": record.get("Owner", {}).get("name"),
                    "created_time": record.get("Created_Time"),
                    "modified_time": record.get("Modified_Time"),
                    "raw_data": record,
                }
            )

        return normalized
