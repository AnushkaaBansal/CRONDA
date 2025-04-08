from typing import Dict, List, Set, Optional
import re
from collections import defaultdict

class TagAnalyzer:
    """Advanced tag analysis and filtering capabilities"""
    
    @staticmethod
    def match_tag_pattern(resource_tags: Dict[str, str], 
                         required_tags: Dict[str, str],
                         case_sensitive: bool = False,
                         partial_match: bool = False) -> bool:
        """
        Advanced tag pattern matching
        
        Args:
            resource_tags: Tags on the resource
            required_tags: Tags to match against
            case_sensitive: Whether to match case sensitively
            partial_match: Allow partial value matches
        """
        if not resource_tags or not required_tags:
            return False
            
        for key, pattern in required_tags.items():
            # Handle case sensitivity
            if not case_sensitive:
                key = key.lower()
                pattern = pattern.lower()
                resource_tags = {k.lower(): v.lower() 
                               for k, v in resource_tags.items()}
            
            # Check if key exists
            if key not in resource_tags:
                return False
                
            # Handle wildcards and patterns
            if pattern.startswith('*') and pattern.endswith('*'):
                if pattern[1:-1] not in resource_tags[key]:
                    return False
            elif pattern.startswith('*'):
                if not resource_tags[key].endswith(pattern[1:]):
                    return False
            elif pattern.endswith('*'):
                if not resource_tags[key].startswith(pattern[:-1]):
                    return False
            elif partial_match:
                if pattern not in resource_tags[key]:
                    return False
            else:
                if pattern != resource_tags[key]:
                    return False
                    
        return True
    
    @staticmethod
    def analyze_tag_patterns(resources: List[Dict]) -> Dict:
        """Analyze tag usage patterns across resources"""
        analysis = {
            'tag_frequency': defaultdict(int),
            'value_frequency': defaultdict(lambda: defaultdict(int)),
            'common_combinations': defaultdict(int),
            'untagged_count': 0,
            'partially_tagged_count': 0,
            'fully_tagged_count': 0,
            'unique_tags': set(),
            'unique_values': defaultdict(set)
        }
        
        required_tags = {'environment', 'project', 'owner'}  # Example required tags
        
        for resource in resources:
            tags = resource.get('labels', {})
            
            # Count untagged/tagged resources
            if not tags:
                analysis['untagged_count'] += 1
                continue
                
            # Check for required tags
            missing_required = required_tags - set(tags.keys())
            if missing_required:
                analysis['partially_tagged_count'] += 1
            else:
                analysis['fully_tagged_count'] += 1
            
            # Analyze individual tags
            for key, value in tags.items():
                analysis['tag_frequency'][key] += 1
                analysis['value_frequency'][key][value] += 1
                analysis['unique_tags'].add(key)
                analysis['unique_values'][key].add(value)
            
            # Analyze tag combinations
            tag_combo = frozenset(tags.items())
            analysis['common_combinations'][tag_combo] += 1
        
        # Convert sets to lists for JSON serialization
        analysis['unique_tags'] = list(analysis['unique_tags'])
        analysis['unique_values'] = {k: list(v) 
                                   for k, v in analysis['unique_values'].items()}
        
        return dict(analysis)
    
    @staticmethod
    def suggest_tag_improvements(resource_tags: Dict[str, str]) -> List[str]:
        """Suggest improvements for resource tags"""
        suggestions = []
        
        # Check for common tag keys
        common_tags = {
            'environment': ['prod', 'dev', 'staging', 'test'],
            'project': None,  # Any value acceptable
            'owner': None,    # Any value acceptable
            'cost-center': None,
            'purpose': None
        }
        
        # Check missing important tags
        for tag, valid_values in common_tags.items():
            if tag not in resource_tags:
                suggestions.append(f"Consider adding '{tag}' tag")
            elif valid_values and resource_tags[tag] not in valid_values:
                suggestions.append(
                    f"'{tag}' value '{resource_tags[tag]}' not in standard values: {valid_values}"
                )
        
        # Check for potentially problematic patterns
        for key, value in resource_tags.items():
            # Check for temporary-looking tags
            if any(temp in key.lower() for temp in ['temp', 'temporary', 'test']):
                suggestions.append(f"Tag '{key}' appears to be temporary")
            
            # Check for empty values
            if not value:
                suggestions.append(f"Tag '{key}' has empty value")
            
            # Check for common typos
            common_keys = ['environment', 'env', 'project', 'proj']
            for common in common_keys:
                if key.lower() != common and key.lower().startswith(common[:2]):
                    suggestions.append(f"Tag '{key}' might be a typo of '{common}'")
        
        return suggestions