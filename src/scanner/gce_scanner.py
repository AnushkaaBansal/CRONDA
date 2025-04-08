from google.cloud import compute_v1
from datetime import datetime, timezone
from typing import List, Dict, Optional
from .base_scanner import BaseResourceScanner
from google.auth import default

class GCEScanner(BaseResourceScanner):
    """Scanner for Google Compute Engine instances"""
    
    def __init__(self, project_id: str):
        super().__init__(project_id)
        credentials, _ = default()
        self.instance_client = compute_v1.InstancesClient(credentials=credentials)
        self.zones_client = compute_v1.ZonesClient(credentials=credentials)
        
    def _list_zones(self) -> List[str]:
        """Get list of all zones in the project"""
        try:
            request = compute_v1.ListZonesRequest(project=self.project_id)
            zones = self.zones_client.list(request=request)
            return [zone.name for zone in zones]
        except Exception as e:
            self.logger.error(f"Error listing zones: {str(e)}")
            return []
        
    def scan_resources(
        self,
        age_threshold_days: int = 30,
        required_tags: Optional[Dict[str, str]] = None,
        max_resources: int = 100
    ) -> List[Dict]:
        """Scan for GCE instances matching criteria"""
        try:
            instances = []
            zones = self._list_zones()
            
            for zone in zones:
                try:
                    request = compute_v1.ListInstancesRequest(
                        project=self.project_id,
                        zone=zone
                    )
                    
                    page_result = self.instance_client.list(request=request)
                    
                    for instance in page_result:
                        # Calculate age in days
                        creation_time = datetime.fromisoformat(instance.creation_timestamp)
                        age_days = (datetime.now(timezone.utc) - creation_time).days
                        
                        # Convert labels to dictionary
                        labels = dict(instance.labels) if instance.labels else {}
                        
                        # Check if instance matches criteria
                        if age_threshold_days > 0 and age_days < age_threshold_days:
                            continue
                            
                        if required_tags and not self._matches_tags(labels, required_tags):
                            continue
                        
                        # Add instance to results
                        instances.append({
                            'name': instance.name,
                            'age_days': age_days,
                            'labels': labels,
                            'zone': zone,
                            'machine_type': instance.machine_type.split('/')[-1],
                            'status': instance.status,
                        })
                        
                        if len(instances) >= max_resources:
                            return instances
                            
                except Exception as e:
                    self.logger.error(f"Error scanning zone {zone}: {str(e)}")
                    continue
            
            return instances
            
        except Exception as e:
            self.logger.error(f"Error scanning GCE instances: {str(e)}")
            raise
    
    def get_resource_details(self, instance_name: str) -> Optional[Dict]:
        """Get detailed information about a specific instance"""
        try:
            # Need to search in all zones
            for zone in self._list_zones():
                try:
                    request = compute_v1.GetInstanceRequest(
                        project=self.project_id,
                        zone=zone,
                        instance=instance_name
                    )
                    instance_detail = self.instance_client.get(request=request)
                    
                    return {
                        'name': instance_detail.name,
                        'id': instance_detail.id,
                        'machine_type': instance_detail.machine_type.split('/')[-1],
                        'zone': zone,
                        'status': instance_detail.status,
                        'creation_timestamp': instance_detail.creation_timestamp,
                        'labels': dict(instance_detail.labels) if instance_detail.labels else {},
                        'network_interfaces': [
                            {
                                'network': ni.network.split('/')[-1],
                                'external_ip': ni.access_configs[0].nat_ip if ni.access_configs else None
                            }
                            for ni in instance_detail.network_interfaces
                        ],
                        'disks': [
                            {
                                'name': disk.source.split('/')[-1],
                                'boot': disk.boot,
                                'auto_delete': disk.auto_delete
                            }
                            for disk in instance_detail.disks
                        ]
                    }
                except Exception:
                    continue
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting instance details: {str(e)}")
            raise