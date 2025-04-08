from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Bucket(BaseModel):
    name: str
    created_at: datetime
    size_bytes: int
    tags: Optional[List[str]] = []

class BucketScanResult(BaseModel):
    total_buckets: int
    candidates_for_deletion: List[Bucket]
    total_size_bytes: int