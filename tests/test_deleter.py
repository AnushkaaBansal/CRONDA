import logging
from src.scanner.gcs_scanner import GCSScanner
from src.scanner.gcs_deleter import GCSDeleter
from src.config.settings import Settings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_scan_and_delete():
    """
    Test scanning and deletion (with dry_run)
    """
    settings = Settings()
    scanner = GCSScanner(settings.PROJECT_ID)
    deleter = GCSDeleter(settings.PROJECT_ID)
    
    logger.info("Starting scan and delete test...")
    
    # First scan for buckets
    results = scanner.scan_old_buckets(
        age_threshold_days=0,  # Set to 0 to find our new test bucket
        max_buckets=5
    )
    
    logger.info(f"Found {len(results)} buckets")
    
    # Try to delete each bucket (in dry_run mode)
    for bucket in results:
        logger.info(f"\nAttempting to delete bucket: {bucket['name']}")
        success = deleter.delete_bucket(
            bucket_name=bucket['name'],
            dry_run=True  # Safe mode - won't actually delete
        )
        if success:
            logger.info(f"Dry run deletion successful for {bucket['name']}")
        else:
            logger.error(f"Dry run deletion failed for {bucket['name']}")

if __name__ == "__main__":
    test_scan_and_delete()