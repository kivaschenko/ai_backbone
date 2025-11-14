"""
Google Sheets Connector
Handles reading and writing data from Google Sheets.
"""

from typing import Dict, Any, List, Optional
import requests
import logging
from .base import BaseConnector

logger = logging.getLogger(__name__)


class GoogleSheetsConnector(BaseConnector):
    """Connector for Google Sheets API integration."""

    BASE_URL = "https://sheets.googleapis.com/v4/spreadsheets"

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Google Sheets connector.

        Args:
            config: Must include client_id, client_secret, refresh_token
        """
        super().__init__(config)
        self.access_token = None

    def authenticate(self) -> bool:
        """Authenticate with Google Sheets API."""
        try:
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
            logger.info("Google Sheets authentication successful")
            return True

        except Exception as e:
            logger.error(f"Google Sheets authentication failed: {str(e)}")
            return False

    def fetch_data(
        self, spreadsheet_id: str, range_name: str, **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Fetch data from a Google Sheet.

        Args:
            spreadsheet_id: The ID of the spreadsheet
            range_name: The A1 notation of the range to retrieve
            **kwargs: Additional parameters

        Returns:
            List of row data
        """
        headers = {"Authorization": f"Bearer {self.access_token}"}
        url = f"{self.BASE_URL}/{spreadsheet_id}/values/{range_name}"

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        data = response.json()
        rows = data.get("values", [])

        logger.info(f"Fetched {len(rows)} rows from Google Sheets")
        return rows

    def normalize_data(self, raw_data: List[List[Any]]) -> List[Dict[str, Any]]:
        """
        Normalize Google Sheets data to unified schema.
        Assumes first row contains headers.

        Args:
            raw_data: Raw row data from Google Sheets

        Returns:
            Normalized data records
        """
        if not raw_data:
            return []

        headers = raw_data[0]
        normalized = []

        for row in raw_data[1:]:
            # Pad row with empty strings if shorter than headers
            padded_row = row + [""] * (len(headers) - len(row))

            record = {
                "source": "google_sheets",
                "data": dict(zip(headers, padded_row)),
                "raw_data": row,
            }
            normalized.append(record)

        return normalized

    def write_data(
        self, spreadsheet_id: str, range_name: str, values: List[List[Any]]
    ) -> bool:
        """
        Write data to a Google Sheet.

        Args:
            spreadsheet_id: The ID of the spreadsheet
            range_name: The A1 notation of the range to write to
            values: 2D array of values to write

        Returns:
            bool: True if write successful
        """
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        url = f"{self.BASE_URL}/{spreadsheet_id}/values/{range_name}"

        params = {"valueInputOption": "RAW"}
        body = {"values": values}

        try:
            response = requests.put(url, headers=headers, params=params, json=body)
            response.raise_for_status()

            logger.info(f"Wrote {len(values)} rows to Google Sheets")
            return True

        except Exception as e:
            logger.error(f"Failed to write to Google Sheets: {str(e)}")
            return False
