from google.cloud import storage
from datetime import datetime

def create_tagged_bucket():
    """Create a test bucket with tags"""
    client = storage.Client()
    
    # Create bucket with timestamp
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    bucket_name = f"cronda-test-{timestamp}"
    
    try:
        bucket = client.create_bucket(bucket_name)
        
        # Add labels/tags to the bucket
        bucket.labels = {
            'purpose': 'test',
            'environment': 'development',
            'project': 'cronda'
        }
        bucket.patch()
        
        print(f"Created tagged bucket: {bucket_name}")
        print(f"Tags: {bucket.labels}")
        return bucket_name
        
    except Exception as e:
        print(f"Error creating bucket: {str(e)}")
        return None

if __name__ == "__main__":
    create_tagged_bucket()