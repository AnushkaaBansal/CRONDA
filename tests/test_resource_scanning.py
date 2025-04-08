import logging
from src.scanner.resource_factory import ResourceFactory
from src.config.settings import Settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_resource_scanning():
    """Test the resource scanning framework"""
    settings = Settings()
    
    # Test GCS Scanner through factory
    logger.info("Testing GCS resource scanning...")
    scanner = ResourceFactory.get_scanner('gcs', settings.PROJECT_ID)
    
    if scanner:
        # Scan with both age and tag filters
        results = scanner.scan_resources(
            age_threshold_days=0,
            required_tags={'purpose': 'test'},
            max_resources=5
        )
        
        logger.info(f"\nFound {len(results)} matching resources:")
        for resource in results:
            logger.info("\nResource Details:")
            logger.info(f"Name: {resource['name']}")
            logger.info(f"Age: {resource['age_days']} days")
            logger.info(f"Labels: {resource['labels']}")
            
            # Get detailed information
            details = scanner.get_resource_details(resource['name'])
            if details:
                logger.info("Additional Details:")
                logger.info(f"Location: {details.get('location')}")
                logger.info(f"Storage Class: {details.get('storage_class')}")
            logger.info("-" * 50)
    else:
        logger.error("Failed to create GCS scanner")

if __name__ == "__main__":
    test_resource_scanning()