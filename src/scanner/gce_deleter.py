from google.cloud import compute_v1
from typing import Dict, List
from .base_scanner import BaseResourceScanner  # Changed to match your project structure

class GCEDeleter(BaseResourceScanner):  # Changed from BaseResourceDeleter to BaseResourceScanner
    """Deleter for Google Compute Engine instances"""
    
    def __init__(self, project_id: str):
        super().__init__(project_id)
        self.client = compute_v1.InstancesClient()
    
    def batch_delete(self, instance_names: List[str], dry_run: bool = True) -> Dict[str, List[str]]:
        """Delete multiple instances"""
        results = {
            'successful': [],
            'failed': []
        }
        
        if dry_run:
            self.logger.info(f"Dry run: Would delete instances: {instance_names}")
            results['successful'] = instance_names
            return results
            
        for instance_name in instance_names:
            try:
                # Need to get zone first
                request = compute_v1.ListInstancesRequest(
                    project=self.project_id,
                    zone='-'
                )
                
                instance_found = False
                for instance in self.client.list(request=request):
                    if instance.name == instance_name:
                        zone = instance.zone.split('/')[-1]
                        instance_found = True
                        
                        # Delete the instance
                        delete_request = compute_v1.DeleteInstanceRequest(
                            project=self.project_id,
                            zone=zone,
                            instance=instance_name
                        )
                        
                        operation = self.client.delete(request=delete_request)
                        operation.result()  # Wait for deletion to complete
                        
                        results['successful'].append(instance_name)
                        break
                
                if not instance_found:
                    results['failed'].append(instance_name)
                    self.logger.error(f"Instance not found: {instance_name}")
                    
            except Exception as e:
                results['failed'].append(instance_name)
                self.logger.error(f"Error deleting instance {instance_name}: {str(e)}")
        
        return results

    # Adding required methods from BaseResourceScanner
    def scan_resources(self, age_threshold_days: int = 30, required_tags: Dict[str, str] = None, max_resources: int = 100) -> List[Dict]:
        """Placeholder for scan_resources - not used in deleter"""
        return []

    def get_resource_details(self, resource_name: str) -> Dict:
        """Placeholder for get_resource_details - not used in deleter"""
        return {}