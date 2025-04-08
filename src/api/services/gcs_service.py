from google.cloud import storage
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging
import os

logger = logging.getLogger(__name__)

class GCSService:
    def __init__(self):
        self.storage_client = storage.Client()

    def get_project_buckets(self, project_id: str = None) -> List[Dict[str, Any]]:
        """Get all buckets in the project with their metadata"""
        try:
            buckets = []
            for bucket in self.storage_client.list_buckets(project=project_id):
                # Get bucket metadata
                metadata = {
                    "name": bucket.name,
                    "created_at": bucket.time_created.isoformat() if bucket.time_created else None,
                    "updated_at": bucket.updated.isoformat() if bucket.updated else None,
                    "size_bytes": sum(blob.size for blob in bucket.list_blobs()),
                    "location": bucket.location,
                    "storage_class": bucket.storage_class,
                    "labels": bucket.labels or {},
                    "lifecycle_rules": bucket.lifecycle_rules or [],
                    "versioning_enabled": bucket.versioning_enabled
                }
                buckets.append(metadata)
            return buckets
        except Exception as e:
            logger.error(f"Error listing buckets: {str(e)}")
            raise

    def analyze_deletion_candidates(self, days: int = 30, min_size: int = 0) -> Dict[str, Any]:
        """Analyze and return buckets that are candidates for deletion"""
        try:
            all_buckets = self.get_project_buckets()
            cutoff_date = datetime.now() - timedelta(days=days)
            
            candidates = []
            total_size = 0
            
            for bucket in all_buckets:
                created_at = datetime.fromisoformat(bucket["created_at"]) if bucket["created_at"] else None
                if created_at and created_at < cutoff_date and bucket["size_bytes"] >= min_size:
                    candidates.append(bucket)
                    total_size += bucket["size_bytes"]
            
            return {
                "total_buckets": len(candidates),
                "candidates_for_deletion": candidates,
                "total_size_bytes": total_size,
                "analysis_timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error analyzing deletion candidates: {str(e)}")
            raise

    def delete_bucket(self, bucket_name: str, dry_run: bool = True) -> Dict[str, str]:
        """Delete a specific bucket with safety checks"""
        try:
            bucket = self.storage_client.get_bucket(bucket_name)
            
            # Safety checks
            if not dry_run:
                # Check if bucket is empty
                blobs = list(bucket.list_blobs())
                if blobs:
                    return {
                        "status": "error",
                        "message": f"Bucket {bucket_name} is not empty. Please empty it first."
                    }
                
                # Perform deletion
                bucket.delete()
                logger.info(f"Successfully deleted bucket: {bucket_name}")
                return {
                    "status": "success",
                    "message": f"Deleted bucket {bucket_name}"
                }
            
            return {
                "status": "dry_run",
                "message": f"Dry run: Would delete bucket {bucket_name}"
            }
        except Exception as e:
            logger.error(f"Error deleting bucket {bucket_name}: {str(e)}")
            raise

    def batch_delete_buckets(self, bucket_names: List[str], dry_run: bool = True) -> Dict[str, Any]:
        """Delete multiple buckets in batch"""
        results = {
            "success": [],
            "failed": [],
            "skipped": []
        }
        
        for bucket_name in bucket_names:
            try:
                result = self.delete_bucket(bucket_name, dry_run)
                if result["status"] == "success":
                    results["success"].append(bucket_name)
                elif result["status"] == "error":
                    results["failed"].append({
                        "name": bucket_name,
                        "reason": result["message"]
                    })
                else:  # dry run
                    results["skipped"].append(bucket_name)
            except Exception as e:
                results["failed"].append({
                    "name": bucket_name,
                    "reason": str(e)
                })
        
        return {
            "status": "completed",
            "results": results,
            "summary": {
                "total": len(bucket_names),
                "success": len(results["success"]),
                "failed": len(results["failed"]),
                "skipped": len(results["skipped"])
            }
        }