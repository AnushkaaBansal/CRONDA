from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import logging

class BaseResourceScanner(ABC):
    """Base class for all GCP resource scanners"""
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.logger = logging.getLogger(self.__class__.__name__)
        
    @abstractmethod
    def scan_resources(self, 
                      age_threshold_days: int,
                      required_tags: Optional[Dict[str, str]] = None,
                      max_resources: int = 10) -> List[Dict]:
        """Base method for scanning resources"""
        pass
    
    @abstractmethod
    def get_resource_details(self, resource_id: str) -> Optional[Dict]:
        """Get detailed information about a specific resource"""
        pass
    
    def _validate_free_tier_limits(self, count: int, limit: int) -> int:
        """Ensure we stay within free tier limits"""
        if count > limit:
            self.logger.warning(f"Limiting scan to {limit} resources for free tier safety")
            return limit
        return count