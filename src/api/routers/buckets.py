from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from src.api.services.gcs_service import GCSService
from datetime import datetime
from pydantic import BaseModel

router = APIRouter(prefix="/buckets", tags=["buckets"])
gcs_service = GCSService()

class BatchDeleteRequest(BaseModel):
    bucket_names: List[str]
    dry_run: bool = True

@router.get("/")
async def list_buckets(
    days: Optional[int] = Query(30, gt=0, description="Age in days to filter buckets"),
    min_size: Optional[int] = Query(0, ge=0, description="Minimum size in bytes")
):
    """List all buckets that are candidates for deletion"""
    try:
        return gcs_service.analyze_deletion_candidates(days, min_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/all")
async def list_all_buckets():
    """List all buckets in the project"""
    try:
        return gcs_service.get_project_buckets()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{bucket_name}")
async def delete_bucket(
    bucket_name: str, 
    dry_run: bool = Query(True, description="If true, only simulate the deletion")
):
    """Delete a specific bucket"""
    try:
        result = gcs_service.delete_bucket(bucket_name, dry_run)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch-delete")
async def batch_delete_buckets(request: BatchDeleteRequest):
    """Delete multiple buckets in batch"""
    try:
        return gcs_service.batch_delete_buckets(request.bucket_names, request.dry_run)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))