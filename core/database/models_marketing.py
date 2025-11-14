"""
Marketing Data Models
Unified schema for marketing and advertising data.
"""

from sqlalchemy import Column, String, Float, DateTime, JSON, Integer, Date
from sqlalchemy.sql import func
from .connection import Base


class MarketingCampaign(Base):
    """Campaign performance data from advertising platforms."""

    __tablename__ = "marketing_campaigns"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(String(100), nullable=False, index=True)
    source = Column(
        String(50), nullable=False, index=True
    )  # google_ads, meta_ads, etc.

    # Campaign details
    campaign_name = Column(String(255), index=True)
    campaign_status = Column(String(50))
    ad_group = Column(String(255))

    # Metrics
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    spend = Column(Float, default=0.0)
    conversions = Column(Integer, default=0)
    conversion_value = Column(Float, default=0.0)

    # Calculated metrics
    ctr = Column(Float)  # Click-through rate
    cpc = Column(Float)  # Cost per click
    cpa = Column(Float)  # Cost per acquisition
    roas = Column(Float)  # Return on ad spend

    # Date range
    date = Column(Date, index=True)
    date_start = Column(Date)
    date_end = Column(Date)

    # Timestamps
    synced_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Raw data
    raw_data = Column(JSON)

    def __repr__(self):
        return f"<MarketingCampaign(source={self.source}, name={self.campaign_name}, spend={self.spend})>"

    def calculate_metrics(self):
        """Calculate derived metrics."""
        if self.impressions > 0:
            self.ctr = (self.clicks / self.impressions) * 100

        if self.clicks > 0:
            self.cpc = self.spend / self.clicks

        if self.conversions > 0:
            self.cpa = self.spend / self.conversions

        if self.spend > 0 and self.conversion_value > 0:
            self.roas = self.conversion_value / self.spend


class MarketingAdCreative(Base):
    """Ad creative performance data."""

    __tablename__ = "marketing_ad_creatives"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(String(100), nullable=False, index=True)
    source = Column(String(50), nullable=False, index=True)

    # Creative details
    campaign_id = Column(String(100), index=True)
    ad_name = Column(String(255))
    ad_type = Column(String(50))  # image, video, carousel, etc.

    # Content
    headline = Column(String(500))
    description = Column(String(1000))
    image_url = Column(String(500))
    video_url = Column(String(500))

    # Performance
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    spend = Column(Float, default=0.0)
    conversions = Column(Integer, default=0)

    # Date
    date = Column(Date, index=True)

    # Timestamps
    synced_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Raw data
    raw_data = Column(JSON)

    def __repr__(self):
        return f"<MarketingAdCreative(name={self.ad_name}, clicks={self.clicks})>"
