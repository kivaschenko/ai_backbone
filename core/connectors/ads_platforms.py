"""
Ads Platform Connectors
Handles data fetching from Google Ads and Meta (Facebook) Ads.
"""

from typing import Dict, Any, List, Optional
import requests
import logging
from .base import BaseConnector

logger = logging.getLogger(__name__)


class GoogleAdsConnector(BaseConnector):
    """Connector for Google Ads API integration."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Google Ads connector.

        Args:
            config: Must include developer_token, client_id, client_secret,
                    refresh_token, customer_id
        """
        super().__init__(config)
        self.access_token = None

    def authenticate(self) -> bool:
        """Authenticate with Google Ads API."""
        try:
            # OAuth 2.0 token refresh
            auth_url = "https://oauth2.googleapis.com/token"
            data = {
                "client_id": self.config["client_id"],
                "client_secret": self.config["client_secret"],
                "refresh_token": self.config["refresh_token"],
                "grant_type": "refresh_token",
            }

            response = requests.post(auth_url, data=data)
            response.raise_for_status()

            self.access_token = response.json()["access_token"]
            logger.info("Google Ads authentication successful")
            return True

        except Exception as e:
            logger.error(f"Google Ads authentication failed: {str(e)}")
            return False

    def fetch_data(self, **kwargs) -> List[Dict[str, Any]]:
        """Fetch campaign and ad performance data from Google Ads."""
        # Placeholder for Google Ads API query
        # Actual implementation would use Google Ads API library
        logger.info("Fetching Google Ads data")
        return []

    def normalize_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize Google Ads data to unified schema."""
        normalized = []

        for record in raw_data:
            normalized.append(
                {
                    "id": record.get("id"),
                    "source": "google_ads",
                    "campaign_name": record.get("campaign", {}).get("name"),
                    "ad_group": record.get("ad_group", {}).get("name"),
                    "impressions": record.get("metrics", {}).get("impressions"),
                    "clicks": record.get("metrics", {}).get("clicks"),
                    "cost": record.get("metrics", {}).get("cost_micros", 0) / 1_000_000,
                    "conversions": record.get("metrics", {}).get("conversions"),
                    "date": record.get("segments", {}).get("date"),
                    "raw_data": record,
                }
            )

        return normalized


class MetaAdsConnector(BaseConnector):
    """Connector for Meta (Facebook) Ads API integration."""

    BASE_URL = "https://graph.facebook.com/v18.0"

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Meta Ads connector.

        Args:
            config: Must include access_token, ad_account_id
        """
        super().__init__(config)
        self.access_token = config.get("access_token")
        self.ad_account_id = config.get("ad_account_id")

    def authenticate(self) -> bool:
        """Verify access token is valid."""
        try:
            url = f"{self.BASE_URL}/me"
            params = {"access_token": self.access_token}

            response = requests.get(url, params=params)
            response.raise_for_status()

            logger.info("Meta Ads authentication successful")
            return True

        except Exception as e:
            logger.error(f"Meta Ads authentication failed: {str(e)}")
            return False

    def fetch_data(self, **kwargs) -> List[Dict[str, Any]]:
        """Fetch campaign insights from Meta Ads."""
        try:
            url = f"{self.BASE_URL}/act_{self.ad_account_id}/insights"

            params = {
                "access_token": self.access_token,
                "level": kwargs.get("level", "campaign"),
                "fields": kwargs.get(
                    "fields", "campaign_name,impressions,clicks,spend,actions"
                ),
                "time_range": kwargs.get(
                    "time_range", {"since": "2024-01-01", "until": "2024-12-31"}
                ),
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json().get("data", [])
            logger.info(f"Fetched {len(data)} records from Meta Ads")
            return data

        except Exception as e:
            logger.error(f"Failed to fetch Meta Ads data: {str(e)}")
            return []

    def normalize_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize Meta Ads data to unified schema."""
        normalized = []

        for record in raw_data:
            normalized.append(
                {
                    "id": record.get("campaign_id"),
                    "source": "meta_ads",
                    "campaign_name": record.get("campaign_name"),
                    "impressions": int(record.get("impressions", 0)),
                    "clicks": int(record.get("clicks", 0)),
                    "spend": float(record.get("spend", 0)),
                    "conversions": self._extract_conversions(record.get("actions", [])),
                    "date_start": record.get("date_start"),
                    "date_stop": record.get("date_stop"),
                    "raw_data": record,
                }
            )

        return normalized

    def _extract_conversions(self, actions: List[Dict]) -> int:
        """Extract conversion count from actions array."""
        for action in actions:
            if action.get("action_type") == "purchase":
                return int(action.get("value", 0))
        return 0
