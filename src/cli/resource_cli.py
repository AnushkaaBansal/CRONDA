import click
from datetime import datetime, timezone
from typing import Dict
import json
from ..scanner.resource_factory import ResourceFactory
from ..scanner.gcs_deleter import GCSDeleter
from ..scanner.gce_deleter import GCEDeleter
from ..config.settings import Settings

def _get_tags_summary(resources: list) -> Dict:
    """Analyze tag usage across resources"""
    tag_counts = {}
    for resource in resources:
        for key, value in (resource.get('labels') or {}).items():
            if key not in tag_counts:
                tag_counts[key] = {}
            if value not in tag_counts[key]:
                tag_counts[key][value] = 0
            tag_counts[key][value] += 1
    return tag_counts

def _display_text_stats(stats_data: Dict):
    """Display statistics in text format"""
    click.echo("\nResource Statistics Summary:")
    click.echo("-" * 50)
    click.echo(f"Total Resources: {stats_data['total_count']}")
    click.echo(f"Tagged Resources: {stats_data['tagged_resources']}")
    click.echo(f"Untagged Resources: {stats_data['untagged_resources']}")
    
    click.echo("\nAge Distribution:")
    click.echo("-" * 20)
    click.echo(f"  0-30 days: {stats_data['age_distribution']['0_30_days']}")
    click.echo(f"  31-60 days: {stats_data['age_distribution']['31_60_days']}")
    click.echo(f"  60+ days: {stats_data['age_distribution']['60_plus_days']}")
    
    if stats_data['tags_summary']:
        click.echo("\nTag Usage:")
        click.echo("-" * 20)
        for tag_key, values in stats_data['tags_summary'].items():
            click.echo(f"\n{tag_key}:")
            for value, count in values.items():
                click.echo(f"  {value}: {count} resources")
    
    click.echo(f"\nReport Generated: {stats_data['timestamp']}")

def _find_redundant_tags(resources: list) -> Dict:
    """Find potentially redundant or inconsistent tags"""
    tag_patterns = {}
    redundant = {}
    
    # Analyze tag patterns
    for resource in resources:
        labels = resource.get('labels', {})
        if not labels:
            continue
            
        # Check for similar tag keys (case insensitive)
        for key in labels:
            key_lower = key.lower()
            if key_lower not in tag_patterns:
                tag_patterns[key_lower] = set()
            tag_patterns[key_lower].add(key)
            
        # Check for similar tag values
        for key, value in labels.items():
            if key not in redundant:
                redundant[key] = {}
            if value not in redundant[key]:
                redundant[key][value] = 0
            redundant[key][value] += 1
    
    # Find potential issues
    issues = {
        'similar_keys': {k: list(v) for k, v in tag_patterns.items() if len(v) > 1},
        'single_use_tags': {
            key: {val: count for val, count in values.items() if count == 1}
            for key, values in redundant.items()
        }
    }
    
    return issues

def _display_recommendations(recommendations: Dict):
    """Display cleanup recommendations"""
    click.echo("\nCleanup Recommendations:")
    click.echo("-" * 50)
    
    # Untagged resources
    if recommendations['untagged_resources']:
        click.echo("\n1. Untagged Resources:")
        click.echo("   Consider adding tags to these resources for better management:")
        for resource in recommendations['untagged_resources']:
            click.echo(f"   - {resource['name']} (Age: {resource['age_days']} days)")
    
    # Old resources
    if recommendations['old_resources']:
        click.echo("\n2. Old Resources:")
        click.echo("   These resources might be candidates for cleanup:")
        for resource in recommendations['old_resources']:
            click.echo(f"   - {resource['name']} (Age: {resource['age_days']} days)")
            if resource.get('labels'):
                click.echo(f"     Tags: {resource['labels']}")
    
    # Tag issues
    tag_issues = recommendations['redundant_tags']
    if tag_issues['similar_keys']:
        click.echo("\n3. Inconsistent Tag Keys:")
        click.echo("   These tag keys might need standardization:")
        for base_key, variants in tag_issues['similar_keys'].items():
            click.echo(f"   - Found variations of '{base_key}': {', '.join(variants)}")
    
    if tag_issues['single_use_tags']:
        click.echo("\n4. Single-Use Tags:")
        click.echo("   These tags are used only once and might need review:")
        for key, values in tag_issues['single_use_tags'].items():
            if values:
                click.echo(f"   - {key}: {', '.join(values.keys())}")

@click.group()
def cli():
    """CRONDA - Multi-Resource Management CLI"""
    pass

@cli.command()
@click.option('--resource-type', type=click.Choice(['gcs', 'gce']), default='gcs',
              help='Type of resource to scan')
@click.option('--age-days', default=30, help='Age threshold in days')
@click.option('--tag', multiple=True, help='Tags to filter by (format: key=value)')
@click.option('--case-sensitive/--no-case-sensitive', default=False,
              help='Case sensitive tag matching')
@click.option('--partial-match/--no-partial-match', default=False,
              help='Allow partial tag value matches')
@click.option('--analyze-tags/--no-analyze-tags', default=False,
              help='Show detailed tag analysis')
def scan(resource_type, age_days, tag, case_sensitive, partial_match, analyze_tags):
    """Scan resources of specified type with enhanced tag filtering"""
    settings = Settings()
    scanner = ResourceFactory.get_scanner(resource_type, settings.PROJECT_ID)
    
    # Convert tags to dictionary
    tags = dict(t.split('=') for t in tag) if tag else None
    
    # Set up tag options
    tag_options = {
        'case_sensitive': case_sensitive,
        'partial_match': partial_match
    }
    
    click.echo(f"\nScanning with options: {tag_options}")
    click.echo("-" * 50)
    
    results = scanner.scan_resources(
        age_threshold_days=age_days,
        required_tags=tags,
        max_resources=settings.MAX_BUCKETS_PER_SCAN,
        tag_options=tag_options
    )
    
    click.echo(f"\nFound {len(results)} {resource_type} resources:")
    for resource in results:
        click.echo("\nResource Details:")
        click.echo("-" * 20)
        click.echo(f"Name: {resource['name']}")
        click.echo(f"Age: {resource['age_days']} days")
        click.echo(f"Labels: {resource['labels']}")
        
        if resource.get('tag_suggestions'):
            click.echo("\nTag Suggestions:")
            click.echo("-" * 20)
            for category, suggestions in resource['tag_suggestions'].items():
                click.echo(f"\n  {category}:")
                for suggestion in suggestions:
                    click.echo(f"    - {suggestion}")
    
    if analyze_tags and results:
        analysis = scanner.analyze_resource_tags(results)
        click.echo("\nTag Analysis:")
        click.echo("-" * 50)
        click.echo(f"Total Resources: {len(results)}")
        click.echo(f"Untagged Resources: {analysis['untagged_count']}")
        click.echo(f"Partially Tagged: {analysis['partially_tagged_count']}")
        click.echo(f"Fully Tagged: {analysis['fully_tagged_count']}")
        
        if analysis.get('tag_frequency'):
            click.echo("\nMost Common Tags:")
            click.echo("-" * 20)
            for tag, count in sorted(
                analysis['tag_frequency'].items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]:
                click.echo(f"  {tag}: {count} resources")

@cli.command()
@click.argument('resource-name')
@click.option('--resource-type', type=click.Choice(['gcs', 'gce']), default='gcs',
              help='Type of resource')
def details(resource_name, resource_type):
    """Get detailed information about a specific resource"""
    settings = Settings()
    scanner = ResourceFactory.get_scanner(resource_type, settings.PROJECT_ID)
    
    details = scanner.get_resource_details(resource_name)
    if details:
        click.echo("\nDetailed Resource Information:")
        click.echo("-" * 30)
        for key, value in details.items():
            if key == 'tag_suggestions':
                click.echo("\nTag Suggestions:")
                click.echo("-" * 20)
                for category, suggestions in value.items():
                    click.echo(f"\n  {category}:")
                    for suggestion in suggestions:
                        click.echo(f"    - {suggestion}")
            else:
                click.echo(f"{key}: {value}")
    else:
        click.echo(f"Resource {resource_name} not found")

@cli.command()
@click.option('--resource-type', type=click.Choice(['gcs', 'gce']), default='gcs',
              help='Type of resource to delete')
@click.option('--age-days', default=30, help='Age threshold in days')
@click.option('--tag', multiple=True, help='Tags to filter by (format: key=value)')
@click.option('--dry-run/--no-dry-run', default=True,
              help='Simulate deletion without actually deleting')
def batch_delete(resource_type, age_days, tag, dry_run):
    """Delete multiple resources based on criteria"""
    settings = Settings()
    scanner = ResourceFactory.get_scanner(resource_type, settings.PROJECT_ID)
    
    # Get appropriate deleter based on resource type
    if resource_type == 'gcs':
        deleter = GCSDeleter(settings.PROJECT_ID)
    elif resource_type == 'gce':
        deleter = GCEDeleter(settings.PROJECT_ID)
    else:
        click.echo(f"Unsupported resource type: {resource_type}")
        return
    
    # Convert tags to dictionary
    tags = dict(t.split('=') for t in tag) if tag else None
    
    # First scan for matching resources
    resources = scanner.scan_resources(
        age_threshold_days=age_days,
        required_tags=tags,
        max_resources=settings.MAX_BUCKETS_PER_SCAN
    )
    
    if not resources:
        click.echo("No matching resources found")
        return
        
    # Show what will be deleted
    click.echo("\nResources to Delete:")
    click.echo("-" * 20)
    for resource in resources:
        click.echo(f"- {resource['name']}")
        if resource.get('labels'):
            click.echo(f"  Labels: {resource['labels']}")
        
    # Confirm deletion
    if not dry_run:
        if not click.confirm("\nDo you want to proceed with deletion?"):
            click.echo("Operation cancelled")
            return
    
    # Perform deletion based on resource type
    if resource_type == 'gcs':
        results = deleter.batch_delete(
            bucket_names=[r['name'] for r in resources],
            dry_run=dry_run
        )
    else:  # gce
        results = deleter.batch_delete(
            instance_names=[r['name'] for r in resources],
            dry_run=dry_run
        )
    
    # Show results
    click.echo("\nOperation Results:")
    click.echo("-" * 20)
    click.echo(f"Successful: {len(results['successful'])}")
    click.echo(f"Failed: {len(results['failed'])}")

@cli.command()
@click.option('--resource-type', type=click.Choice(['gcs', 'gce']), default='gcs',
              help='Type of resource to analyze')
@click.option('--output-format', type=click.Choice(['text', 'json']), default='text',
              help='Output format for statistics')
def stats(resource_type, output_format):
    """Get statistics about resources"""
    settings = Settings()
    scanner = ResourceFactory.get_scanner(resource_type, settings.PROJECT_ID)
    
    # Get all resources (within free tier limits)
    resources = scanner.scan_resources(
        age_threshold_days=0,  # Get all resources
        max_resources=settings.MAX_BUCKETS_PER_SCAN
    )
    
    # Calculate statistics
    stats_data = {
        'total_count': len(resources),
        'tagged_resources': len([r for r in resources if r.get('labels')]),
        'untagged_resources': len([r for r in resources if not r.get('labels')]),
        'age_distribution': {
            '0_30_days': len([r for r in resources if r['age_days'] <= 30]),
            '31_60_days': len([r for r in resources if 30 < r['age_days'] <= 60]),
            '60_plus_days': len([r for r in resources if r['age_days'] > 60])
        },
        'tags_summary': _get_tags_summary(resources),
        'timestamp': datetime.now(timezone.utc).isoformat()
    }
    
    if output_format == 'json':
        click.echo(json.dumps(stats_data, indent=2))
    else:
        _display_text_stats(stats_data)

@cli.command()
@click.option('--resource-type', type=click.Choice(['gcs', 'gce']), default='gcs',
              help='Type of resource to analyze')
@click.option('--min-age', default=30, help='Minimum age in days for old resource warning')
def recommend(resource_type, min_age):
    """Get cleanup recommendations"""
    settings = Settings()
    scanner = ResourceFactory.get_scanner(resource_type, settings.PROJECT_ID)
    
    # Get all resources
    resources = scanner.scan_resources(
        age_threshold_days=0,  # Get all resources
        max_resources=settings.MAX_BUCKETS_PER_SCAN
    )
    
    if not resources:
        click.echo("No resources found to analyze")
        return
    
    # Generate recommendations
    recommendations = {
        'untagged_resources': [r for r in resources if not r.get('labels')],
        'old_resources': [r for r in resources if r['age_days'] > min_age],
        'redundant_tags': _find_redundant_tags(resources)
    }
    
    _display_recommendations(recommendations)
    
    # Add summary with better formatting
    click.echo("\nSummary:")
    click.echo("-" * 30)
    click.echo(f"Total resources analyzed: {len(resources)}")
    click.echo(f"Untagged resources: {len(recommendations['untagged_resources'])}")
    click.echo(f"Old resources (>{min_age} days): {len(recommendations['old_resources'])}")

if __name__ == '__main__':
    cli()