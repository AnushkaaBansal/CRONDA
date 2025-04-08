from google.cloud import storage
from datetime import datetime

def create_test_buckets():
    """Create test buckets for scanning"""
    client = storage.Client()
    
    # Create test bucket with timestamp to ensure unique name
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    bucket_name = f"cronda-test-{timestamp}"
    
    try:
        bucket = client.create_bucket(bucket_name)
        print(f"Created test bucket: {bucket_name}")
        return bucket_name
    except Exception as e:
        print(f"Error creating bucket: {str(e)}")
        return None

if __name__ == "__main__":
    created_bucket = create_test_buckets()