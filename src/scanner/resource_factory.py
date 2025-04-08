from typing import Optional
from .base_scanner import BaseResourceScanner
from .gcs_scanner import GCSScanner
from .gce_scanner import GCEScanner
from .gcs_deleter import GCSDeleter
from .gce_deleter import GCEDeleter

class ResourceFactory:
    """Factory for creating resource scanners and deleters"""
    
    @staticmethod
    def get_scanner(resource_type: str, project_id: str) -> Optional[BaseResourceScanner]:
        """
        Get appropriate scanner for resource type
        Args:
            resource_type: Type of resource ('gcs', 'gce', etc.)
            project_id: GCP project ID
        """
        scanners = {
            'gcs': GCSScanner,
            'gce': GCEScanner,  # Added GCE scanner
        }
        
        scanner_class = scanners.get(resource_type.lower())
        if scanner_class:
            return scanner_class(project_id)
        return None

    @staticmethod
    def get_deleter(resource_type: str, project_id: str):
        """
        Get appropriate deleter for resource type
        Args:
            resource_type: Type of resource ('gcs', 'gce', etc.)
            project_id: GCP project ID
        """
        deleters = {
            'gcs': GCSDeleter,
            'gce': GCEDeleter,  # Added GCE deleter
        }
        
        deleter_class = deleters.get(resource_type.lower())
        if deleter_class:
            return deleter_class(project_id)
        return None