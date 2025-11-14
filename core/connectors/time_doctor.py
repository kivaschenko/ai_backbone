"""
Time Doctor Connector
Handles data fetching from Time Doctor API for time tracking.
"""

from typing import Dict, Any, List, Optional
import requests
import logging
from .base import BaseConnector

logger = logging.getLogger(__name__)


class TimeDoctorConnector(BaseConnector):
    """Connector for Time Doctor API integration."""

    BASE_URL = "https://api2.timedoctor.com/api/1.0"

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Time Doctor connector.

        Args:
            config: Must include access_token, company_id
        """
        super().__init__(config)
        self.access_token = config.get("access_token")
        self.company_id = config.get("company_id")

    def authenticate(self) -> bool:
        """Verify access token is valid."""
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            url = f"{self.BASE_URL}/companies"

            response = requests.get(url, headers=headers)
            response.raise_for_status()

            logger.info("Time Doctor authentication successful")
            return True

        except Exception as e:
            logger.error(f"Time Doctor authentication failed: {str(e)}")
            return False

    def fetch_data(
        self, start_date: str, end_date: str, **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Fetch time tracking data from Time Doctor.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            **kwargs: Additional parameters

        Returns:
            List of time log records
        """
        headers = {"Authorization": f"Bearer {self.access_token}"}
        url = f"{self.BASE_URL}/companies/{self.company_id}/worklogs"

        params = {
            "start": start_date,
            "end": end_date,
            "user_ids": kwargs.get("user_ids", "all"),
        }

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        data = response.json().get("worklogs", [])
        logger.info(f"Fetched {len(data)} work log records from Time Doctor")
        return data

    def normalize_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normalize Time Doctor data to unified schema.

        Args:
            raw_data: Raw data from Time Doctor

        Returns:
            Normalized data records
        """
        normalized = []

        for record in raw_data:
            normalized.append(
                {
                    "id": record.get("id"),
                    "source": "time_doctor",
                    "user_id": record.get("user_id"),
                    "user_name": record.get("user_name"),
                    "task_name": record.get("task_name"),
                    "project_name": record.get("project_name"),
                    "duration_seconds": record.get("length"),
                    "start_time": record.get("start"),
                    "end_time": record.get("end"),
                    "date": record.get("date"),
                    "raw_data": record,
                }
            )

        return normalized
