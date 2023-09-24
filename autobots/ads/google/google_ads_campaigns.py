from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union


class CampaignStatus(Enum):
    ENABLED = "ENABLED"
    PAUSED = "PAUSED"
    REMOVED = "REMOVED"


class AdvertisingChannelType(Enum):
    SEARCH = "SEARCH"
    DISPLAY = "DISPLAY"
    SHOPPING = "SHOPPING"
    VIDEO = "VIDEO"
    APP = "APP"


class BudgetDeliveryMethod(Enum):
    STANDARD = "STANDARD"
    ACCELERATED = "ACCELERATED"


class AdGroupStatus(Enum):
    ENABLED = "ENABLED"
    PAUSED = "PAUSED"
    REMOVED = "REMOVED"

class AdStatusEnum(str, Enum):
    ENABLED = "ENABLED"
    PAUSED = "PAUSED"
    REMOVED = "REMOVED"

# Define individual bidding strategy configurations as Pydantic models based on the Google Ads API documentation

# Manual CPC
class ManualCPC(BaseModel):
    enhanced_cpc_opt_in: Optional[bool] = Field(default=True, description="Enhanced CPC opt-in for MANUAL_CPC strategy.")

# Target CPA
class TargetCPA(BaseModel):
    target_cpa_micros: Optional[int] = Field(description="Average CPA target. This target should be greater than 0.")

# Target ROAS
class TargetROAS(BaseModel):
    target_roas: Optional[float] = Field(description="Desired return on ad spend (ROAS) target. Value should be between 0.01 and 10.0.")
    cpc_bid_ceiling_micros: Optional[int] = Field(description="Maximum CPC bid ceiling. This bid should be greater than 0.")
    cpc_bid_floor_micros: Optional[int] = Field(description="Minimum CPC bid floor. This bid should be greater than 0.")

# Maximize Conversions
class MaximizeConversions(BaseModel):
    target_cpa_micros: Optional[int] = Field(description="Average CPA target. This target should be greater than 0.")

# Maximize Conversion Value
class MaximizeConversionValue(BaseModel):
    target_roas: Optional[float] = Field(description="Desired return on ad spend (ROAS) target. Value should be between 0.01 and 10.0.")



class CampaignCreate(BaseModel):
    name: str = Field(
        ..., 
        description="Name of the ad campaign.", 
        min_length=3,  
        max_length=255  
    )
    status: CampaignStatus = Field(
        ..., 
        description="Status of the campaign. Valid values: ENABLED, PAUSED, REMOVED."
    )
    advertising_channel_type: AdvertisingChannelType = Field(
        ..., 
        description="Type of advertising channel. E.g., SEARCH, DISPLAY, SHOPPING, etc."
    )
    budget: float = Field(
        ..., 
        description="Budget for the campaign.", 
        gt=0  # Ensure budget is greater than 0
    )
    budget_delivery_method: Optional[BudgetDeliveryMethod] = Field(
        None, 
        description="Delivery method for budget. Valid values: STANDARD or ACCELERATED."
    )
    bidding_strategy_details: Union[ManualCPC, TargetCPA, TargetROAS, MaximizeConversions, MaximizeConversionValue]
    
    ad_manager_account_id: int
    ad_account_id: int
    

    
class AdGroupCreate(BaseModel):
    name: str = Field(..., description="Name of the ad group.")
    campaign_id: str = Field(..., description="ID of the associated campaign.")
    status: AdGroupStatus = Field(..., description="Status of the ad group. Valid values: ENABLED, PAUSED, REMOVED.")
    bid_amount: float = Field(..., description="Bid amount for the ad group.")
    ad_manager_account_id: int
    ad_account_id: int


class AdCreate(BaseModel):
    ad_group: str = Field(..., description="Resource_name of the associated ad group.")
    headline: str = Field(..., description="Headline of the ad.")
    description: str = Field(..., description="Description of the ad.")
    final_urls: List[str] = Field(..., description="Final URLs for the ad.")
    path1: Optional[str] = Field(None, description="Path 1 for the ad's URL.")
    path2: Optional[str] = Field(None, description="Path 2 for the ad's URL.")

class ResponsiveSearchAdCreate(BaseModel):
    ad_manager_account_id: int = Field(..., description="Ad Manager account ID.")
    ad_account_id: int = Field(..., description="Individual Ad account ID.")
    ad_group_id: int = Field(..., description="Ad Group ID under which the RSA will be created.")
    
    headlines: List[str] = Field(..., description="List of possible headlines for the RSA.")
    descriptions: List[str] = Field(..., description="List of possible descriptions for the RSA.")
    final_url: str = Field(..., description="Final URL for the RSA when clicked.")
    
    path1: Optional[str] = Field(None, description="Path 1 for display URL.")
    path2: Optional[str] = Field(None, description="Path 2 for display URL.")
    
    status: AdStatusEnum = Field(..., description="Status of the RSA.")
    pinned_headlines: Optional[dict] = Field(None, description="Headlines pinned to specific positions.")
    pinned_descriptions: Optional[dict] = Field(None, description="Descriptions pinned to specific positions.")
    
