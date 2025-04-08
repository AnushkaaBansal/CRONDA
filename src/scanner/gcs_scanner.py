from google.cloud import storage
from datetime import datetime, timezone
import logging
from typing import Dict, List, Optional
from ..config.settings import Settings
from .base_scanner import BaseResourceScanner
from .tag_analyzer import TagAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class GCSScanner(BaseResourceScanner):
    def __init__(self, project_id: str):
        super().__init__(project_id)
        self.client = storage.Client(project=project_id)
        self.settings = Settings()
        self.logger = logging.getLogger(__name__)
        # Ensure logger is set to DEBUG level
        self.logger.setLevel(logging.DEBUG)

    def scan_resources(self, 
                      age_threshold_days: int,
                      required_tags: Optional[Dict[str, str]] = None,
                      max_resources: int = 10,
                      tag_options: Optional[Dict] = None) -> List[Dict]:
        """
        Implement resource scanning for GCS buckets with enhanced tag filtering
        """
        self.logger.debug(f"Starting scan_resources with parameters:")
        self.logger.debug(f"  age_threshold_days: {age_threshold_days}")
        self.logger.debug(f"  required_tags: {required_tags}")
        self.logger.debug(f"  max_resources: {max_resources}")
        self.logger.debug(f"  tag_options: {tag_options}")

        results = self.scan_buckets_with_filters(
            age_threshold_days=age_threshold_days,
            required_tags=required_tags,
            max_buckets=max_resources,
            tag_options=tag_options or {}
        )

        # Format suggestions for display
        for result in results:
            if 'tag_suggestions' in result:
                result['formatted_suggestions'] = self._format_suggestions(result['tag_suggestions'])

        return results

    def get_resource_details(self, resource_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific bucket
        """
        try:
            bucket = self.client.get_bucket(resource_id)
            details = {
                'name': bucket.name,
                'created': bucket.time_created,
                'age_days': (datetime.now(timezone.utc) - bucket.time_created).days,
                'labels': bucket.labels or {},
                'location': bucket.location,
                'storage_class': bucket.storage_class
            }
            
            if bucket.labels:
                suggestions = TagAnalyzer.suggest_tag_improvements(bucket.labels)
                categorized = self._categorize_suggestions(suggestions)
                details['tag_suggestions'] = categorized
                details['formatted_suggestions'] = self._format_suggestions(categorized)
            
            return details
        except Exception as e:
            self.logger.error(f"Error getting bucket details: {str(e)}")
            return None

    def scan_buckets_with_filters(
        self,
        age_threshold_days: int = 0,
        required_tags: Optional[Dict[str, str]] = None,
        max_buckets: int = 10,
        tag_options: Optional[Dict] = None
    ):
        """
        Scan buckets with enhanced age and tag filters
        """
        max_buckets = self._validate_free_tier_limits(max_buckets, self.settings.MAX_BUCKETS_PER_SCAN)
        tag_options = tag_options or {}
            
        matching_buckets = []
        try:
            self.logger.info("\n=== Starting Bucket Scan ===")
            self.logger.info(f"Max buckets to scan: {max_buckets}")
            self.logger.info(f"Tag options: {tag_options}")
            self.logger.info(f"Required tags: {required_tags}")
            
            buckets = list(self.client.list_buckets())[:max_buckets]
            self.logger.info(f"Retrieved {len(buckets)} buckets from GCS")
            
            for bucket in buckets:
                self.logger.debug("\n=== Examining Bucket ===")
                self.logger.debug(f"Bucket name: {bucket.name}")
                self.logger.debug(f"Bucket labels: {bucket.labels}")
                
                matches = self._bucket_matches_criteria(
                    bucket, 
                    age_threshold_days, 
                    required_tags, 
                    tag_options
                )
                
                if matches:
                    self.logger.debug(f"✓ Bucket {bucket.name} matches all criteria")
                    bucket_info = {
                        'name': bucket.name,
                        'created': bucket.time_created,
                        'age_days': (datetime.now(timezone.utc) - bucket.time_created).days,
                        'labels': bucket.labels or {},
                        'size_bytes': self._get_bucket_size(bucket)
                    }
                    
                    if bucket.labels:
                        suggestions = TagAnalyzer.suggest_tag_improvements(bucket.labels)
                        categorized = self._categorize_suggestions(suggestions)
                        bucket_info['tag_suggestions'] = categorized
                        
                        # Log categorized suggestions
                        self.logger.debug("\nTag suggestions for bucket:")
                        formatted = self._format_suggestions(categorized)
                        for line in formatted:
                            self.logger.debug(line)
                    
                    matching_buckets.append(bucket_info)
                else:
                    self.logger.debug(f"✗ Bucket {bucket.name} did not match criteria")
                    
        except Exception as e:
            self.logger.error(f"Error during bucket scan: {str(e)}", exc_info=True)
            
        self.logger.info(f"\n=== Scan Complete ===")
        self.logger.info(f"Found {len(matching_buckets)} matching buckets")
        return matching_buckets

    def _bucket_matches_criteria(
        self,
        bucket: storage.Bucket,
        age_threshold_days: int,
        required_tags: Optional[Dict[str, str]],
        tag_options: Optional[Dict] = None
    ) -> bool:
        """Check if bucket matches all filtering criteria with enhanced tag matching"""
        tag_options = tag_options or {}
        current_time = datetime.now(timezone.utc)
        bucket_age = (current_time - bucket.time_created).days
        
        # Check age criteria
        if age_threshold_days > 0 and bucket_age > age_threshold_days:
            self.logger.debug(f"Bucket {bucket.name} excluded due to age: {bucket_age} days")
            return False
        
        # If no tags required, return True
        if not required_tags:
            return True
        
        # Get bucket labels (or empty dict if None)
        bucket_labels = bucket.labels or {}
        
        # Check each required tag
        for tag_key, required_value in required_tags.items():
            # Skip if the bucket has no labels and tags are required
            if not bucket_labels:
                self.logger.debug(f"Bucket {bucket.name} has no labels")
                return False
                
            # Check if the tag exists
            if tag_key not in bucket_labels:
                self.logger.debug(f"Required tag {tag_key} not found in bucket {bucket.name}")
                return False
                
            actual_value = bucket_labels[tag_key]
            
            # Case-sensitive comparison if specified
            if not tag_options.get('case_sensitive', False):
                required_value = required_value.lower()
                actual_value = actual_value.lower()
                
            # Partial match if specified
            if tag_options.get('partial_match', False):
                if required_value not in actual_value:
                    self.logger.debug(f"Tag value '{required_value}' not found in '{actual_value}' for bucket {bucket.name}")
                    return False
            else:
                if required_value != actual_value:
                    self.logger.debug(f"Tag value mismatch for bucket {bucket.name}: expected '{required_value}', got '{actual_value}'")
                    return False
        
        return True

    def _get_bucket_size(self, bucket: storage.Bucket) -> int:
        """Get total size of bucket in bytes"""
        try:
            total_size = 0
            for blob in bucket.list_blobs():
                total_size += blob.size
            return total_size
        except Exception as e:
            self.logger.error(f"Error getting size for bucket {bucket.name}: {str(e)}")
            return 0

    def analyze_resource_tags(self, resources: List[Dict]) -> Dict:
        """Analyze tag patterns across resources"""
        analysis_results = TagAnalyzer.analyze_tag_patterns(resources)
        self.logger.info(f"Tag analysis complete: {len(resources)} resources analyzed")
        return analysis_results

    def _validate_free_tier_limits(self, requested: int, max_allowed: int) -> int:
        """Validate and adjust the number of resources to scan"""
        if requested > max_allowed:
            self.logger.warning(f"Requested {requested} resources exceeds free tier limit of {max_allowed}")
            return max_allowed
        return requested

    def _categorize_suggestions(self, suggestions: List[str]) -> Dict[str, List[str]]:
        """Categorize tag suggestions for better organization"""
        categories = {
            "Value Standardization": [],
            "Missing Tags": [],
            "Naming Conventions": [],
            "Other": []
        }
        
        for suggestion in suggestions:
            if "not in standard values" in suggestion:
                categories["Value Standardization"].append(suggestion)
            elif "Consider adding" in suggestion:
                categories["Missing Tags"].append(suggestion)
            elif "might be a typo" in suggestion:
                categories["Naming Conventions"].append(suggestion)
            else:
                categories["Other"].append(suggestion)
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}

    def _format_suggestions(self, categorized_suggestions: Dict[str, List[str]]) -> List[str]:
        """Format categorized suggestions for display"""
        formatted = []
        for category, items in categorized_suggestions.items():
            formatted.append(f"\n{category}:")
            for item in items:
                formatted.append(f"  - {item}")
        return formatted