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
    Test both scanning and deletion (in dry-run mode)
    """
    settings = Settings()
    
    # Initialize scanner and deleter
    scanner = GCSScanner(settings.PROJECT_ID)
    deleter = GCSDeleter(settings.PROJECT_ID)
    
    # First, let's list all buckets regardless of age
    logger.info("Listing all buckets first...")
    client = scanner.client
    all_buckets = list(client.list_buckets())
    logger.info(f"Total buckets found: {len(all_buckets)}")
    for bucket in all_buckets:
        logger.info(f"Found bucket: {bucket.name}")
    
    # Now test scanning with age threshold of 0
    logger.info("\nStarting age-based bucket scan...")
    buckets = scanner.scan_old_buckets(
        age_threshold_days=0,  # Set to 0 to find newly created buckets
        max_buckets=settings.MAX_BUCKETS_PER_SCAN
    )
    
    # Print scan results
    logger.info(f"\nFound {len(buckets)} buckets matching age criteria:")
    for bucket in buckets:
        print("\nBucket Details:")
        print(f"Name: {bucket['name']}")
        print(f"Age: {bucket['age_days']} days")
        print(f"Created: {bucket['created'].strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 50)
        
        # Test deletion (in dry-run mode)
        logger.info(f"\nTesting deletion for bucket: {bucket['name']}")
        result = deleter.delete_bucket(bucket['name'], dry_run=True)
        if result:
            logger.info("Dry-run deletion successful")
        else:
            logger.error("Dry-run deletion failed")

if __name__ == "__main__":
    test_scan_and_delete()