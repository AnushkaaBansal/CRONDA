import logging
from src.scanner.gcs_scanner import GCSScanner
from src.scanner.gcs_deleter import GCSDeleter
from src.config.settings import Settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_batch_operations():
    """Test batch scanning and deletion"""
    settings = Settings()
    scanner = GCSScanner(settings.PROJECT_ID)
    deleter = GCSDeleter(settings.PROJECT_ID)
    
    # First, scan for buckets with specific tags
    logger.info("Scanning for test buckets...")
    buckets = scanner.scan_buckets_with_filters(
        age_threshold_days=0,
        required_tags={'purpose': 'test'}
    )
    
    if not buckets:
        logger.info("No matching buckets found for batch operation")
        return
        
    # Get bucket names for batch deletion
    bucket_names = [b['name'] for b in buckets]
    
    # Try batch deletion (dry run)
    logger.info("\nTesting batch deletion (dry run)...")
    results = deleter.batch_delete(
        bucket_names=bucket_names,
        dry_run=True,
        max_batch_size=5
    )
    
    # Print results
    logger.info("\nBatch Operation Results:")
    logger.info(f"Total buckets processed: {len(bucket_names)}")
    logger.info(f"Successful operations: {len(results['successful'])}")
    logger.info(f"Failed operations: {len(results['failed'])}")
    
    if results['successful']:
        logger.info("\nSuccessful Operations:")
        for op in results['successful']:
            logger.info(f"Bucket: {op['bucket']}, Status: {op['status']}")
            
    if results['failed']:
        logger.info("\nFailed Operations:")
        for op in results['failed']:
            logger.info(f"Bucket: {op['bucket']}, Error: {op['error']}")

if __name__ == "__main__":
    test_batch_operations()