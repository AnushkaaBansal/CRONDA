import pytest
from src.scanner.gce_scanner import GCEScanner
from src.scanner.gce_deleter import GCEDeleter
from src.config.settings import Settings

def test_gce_scanning():
    settings = Settings()
    scanner = GCEScanner(settings.PROJECT_ID)
    
    # Test basic scanning
    results = scanner.scan_resources(age_threshold_days=0)
    print(f"\nFound {len(results)} GCE instances:")
    for instance in results:
        print(f"\nInstance: {instance['name']}")
        print(f"Zone: {instance['zone']}")
        print(f"Machine Type: {instance['machine_type']}")
        print(f"Status: {instance['status']}")
        print(f"Labels: {instance['labels']}")

def test_gce_details():
    settings = Settings()
    scanner = GCEScanner(settings.PROJECT_ID)
    
    # Get all instances first
    instances = scanner.scan_resources(age_threshold_days=0)
    if instances:
        # Test details for first instance
        details = scanner.get_resource_details(instances[0]['name'])
        print("\nDetailed Instance Information:")
        for key, value in details.items():
            print(f"{key}: {value}")

if __name__ == '__main__':
    test_gce_scanning()
    test_gce_details()