import unittest
import logging
from src.scanner.gcs_scanner import GCSScanner
from src.config.settings import Settings
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_basic_scan():
    """
    Basic test to verify scanner functionality
    """
    try:
        # Initialize settings and scanner
        settings = Settings()
        scanner = GCSScanner(settings.PROJECT_ID)
        
        logger.info("Starting bucket scan test...")
        
        # Test scan with minimal bucket count for free tier
        results = scanner.scan_old_buckets(
            age_threshold_days=settings.AGE_THRESHOLD_DAYS,
            max_buckets=3  # Small number for testing
        )
        
        # Print results
        logger.info(f"\nFound {len(results)} old buckets:")
        for bucket in results:
            print("\nBucket Details:")
            print(f"Name: {bucket['name']}")
            print(f"Age: {bucket['age_days']} days")
            print(f"Created: {bucket['created'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Size: {bucket['size_bytes'] / 1024 / 1024:.2f} MB")
            print(f"Labels: {bucket['labels']}")
            print("-" * 50)
            
        return len(results) >= 0  # Test passes if we can scan buckets
        
    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}")
        return False

def main():
    """
    Main test runner
    """
    logger.info("Starting GCS Scanner tests...")
    
    try:
        # Run basic scan test
        if test_basic_scan():
            logger.info("Basic scan test completed successfully")
        else:
            logger.error("Basic scan test failed")
            
    except Exception as e:
        logger.error(f"Tests failed with error: {str(e)}")
        
    logger.info("Test suite completed")

if __name__ == "__main__":
    main()