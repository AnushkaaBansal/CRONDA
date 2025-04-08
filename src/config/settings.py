from dataclasses import dataclass
from typing import Optional

@dataclass
class Settings:
    # Project settings
    PROJECT_ID: str = "cronda-project"  # Your GCP project ID
    
    # Scanning settings
    AGE_THRESHOLD_DAYS: int = 30  # Buckets older than this will be flagged
    MAX_BUCKETS_PER_SCAN: int = 10  # Limit for free tier
    BUCKET_NAME_PREFIX: Optional[str] = None  # Filter by prefix if needed
    
    # Safety settings
    DRY_RUN: bool = True  # When True, won't actually delete anything
    
    # Free tier limitations
    MAX_DAILY_OPS: int = 4500  # Daily operation limit
    MAX_STORAGE_GB: float = 4.5  # 90% of 5GB free tier limit
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    
    # Scanner settings
    SCAN_BATCH_SIZE: int = 5  # Number of resources to scan in one batch
    
    def __post_init__(self):
        """Validate settings after initialization"""
        if self.MAX_BUCKETS_PER_SCAN > 50:
            raise ValueError("MAX_BUCKETS_PER_SCAN should not exceed 50 for free tier")
        
        if self.MAX_STORAGE_GB > 4.5:
            raise ValueError("MAX_STORAGE_GB should not exceed 4.5GB for free tier")