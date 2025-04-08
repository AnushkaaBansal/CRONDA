from google.cloud import storage
import logging
from typing import List, Dict
from ..config.settings import Settings

class GCSDeleter:
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.client = storage.Client(project=project_id)
        self.settings = Settings()
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def batch_delete(
        self,
        bucket_names: List[str],
        dry_run: bool = True,
        max_batch_size: int = 5
    ) -> Dict[str, List[Dict]]:
        """
        Delete multiple buckets in batch
        Args:
            bucket_names: List of bucket names to delete
            dry_run: If True, only simulate deletion
            max_batch_size: Maximum buckets to delete in one batch (free tier safe)
        Returns:
            Dictionary with successful and failed operations
        """
        if len(bucket_names) > max_batch_size:
            self.logger.warning(f"Limiting batch size to {max_batch_size} for free tier safety")
            bucket_names = bucket_names[:max_batch_size]

        results = {
            'successful': [],
            'failed': []
        }

        for bucket_name in bucket_names:
            try:
                if dry_run:
                    self.logger.info(f"DRY RUN: Would delete bucket {bucket_name}")
                    results['successful'].append({
                        'bucket': bucket_name,
                        'status': 'would_delete',
                        'dry_run': True
                    })
                    continue

                bucket = self.client.get_bucket(bucket_name)
                bucket.delete()
                
                results['successful'].append({
                    'bucket': bucket_name,
                    'status': 'deleted',
                    'dry_run': False
                })
                self.logger.info(f"Successfully deleted bucket: {bucket_name}")

            except Exception as e:
                results['failed'].append({
                    'bucket': bucket_name,
                    'error': str(e)
                })
                self.logger.error(f"Failed to delete bucket {bucket_name}: {str(e)}")

        # Summary
        self.logger.info(f"\nBatch deletion summary:")
        self.logger.info(f"Successful: {len(results['successful'])}")
        self.logger.info(f"Failed: {len(results['failed'])}")

        return results

