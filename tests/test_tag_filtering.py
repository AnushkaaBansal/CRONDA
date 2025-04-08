import logging
from src.scanner.gcs_scanner import GCSScanner
from src.config.settings import Settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_tag_filtering():
    """Test bucket scanning with tag filters"""
    settings = Settings()
    scanner = GCSScanner(settings.PROJECT_ID)
    
    # Test cases
    test_cases = [
        {
            'name': "Age filter only",
            'age_days': 0,
            'tags': None
        },
        {
            'name': "Age and tag filter",
            'age_days': 0,
            'tags': {'purpose': 'test'}
        },
        {
            'name': "Multiple tags",
            'age_days': 0,
            'tags': {'purpose': 'test', 'environment': 'development'}
        }
    ]
    
    # Run test cases
    for test in test_cases:
        logger.info(f"\nRunning test: {test['name']}")
        results = scanner.scan_buckets_with_filters(
            age_threshold_days=test['age_days'],
            required_tags=test['tags']
        )
        
        logger.info(f"Found {len(results)} matching buckets")
        for bucket in results:
            print("\nBucket Details:")
            print(f"Name: {bucket['name']}")
            print(f"Age: {bucket['age_days']} days")
            print(f"Labels: {bucket['labels']}")
            print("-" * 50)

if __name__ == "__main__":
    test_tag_filtering()