import click
import logging
from ..scanner.gcs_scanner import GCSScanner
from ..scanner.gcs_deleter import GCSDeleter
from ..config.settings import Settings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@click.group()
def cli():
    """CRONDA - Cron for Deletion Automation in GCP"""
    pass

@cli.command()
@click.option('--days', default=30, help='Age threshold in days')
@click.option('--max-buckets', default=10, help='Maximum number of buckets to scan')
def scan(days, max_buckets):
    """Scan for old GCS buckets"""
    try:
        settings = Settings()
        scanner = GCSScanner(settings.PROJECT_ID)
        
        click.echo(f"Scanning for buckets older than {days} days...")
        results = scanner.scan_old_buckets(
            age_threshold_days=days,
            max_buckets=max_buckets
        )
        
        if not results:
            click.echo("No old buckets found.")
            return
            
        click.echo(f"\nFound {len(results)} old buckets:")
        for bucket in results:
            click.echo(f"\nBucket: {bucket['name']}")
            click.echo(f"Age: {bucket['age_days']} days")
            click.echo(f"Size: {bucket['size_bytes'] / 1024 / 1024:.2f} MB")
            
    except Exception as e:
        click.echo(f"Error during scan: {str(e)}", err=True)

@cli.command()
@click.argument('bucket_name')
@click.option('--dry-run/--no-dry-run', default=True, 
              help='Dry run mode (default: True)')
def delete(bucket_name, dry_run):
    """Delete a specific GCS bucket"""
    try:
        settings = Settings()
        deleter = GCSDeleter(settings.PROJECT_ID)
        
        if dry_run:
            click.echo(f"DRY RUN: Would delete bucket {bucket_name}")
        else:
            click.echo(f"Deleting bucket {bucket_name}...")
            
        success = deleter.delete_bucket(bucket_name, dry_run=dry_run)
        
        if success:
            click.echo("Operation completed successfully")
        else:
            click.echo("Operation failed", err=True)
            
    except Exception as e:
        click.echo(f"Error during deletion: {str(e)}", err=True)

@cli.command()
@click.option('--days', default=30, help='Age threshold in days')
@click.option('--dry-run/--no-dry-run', default=True, 
              help='Dry run mode (default: True)')
def cleanup(days, dry_run):
    """Scan and delete old buckets"""
    try:
        settings = Settings()
        scanner = GCSScanner(settings.PROJECT_ID)
        deleter = GCSDeleter(settings.PROJECT_ID)
        
        click.echo(f"Scanning for buckets older than {days} days...")
        results = scanner.scan_old_buckets(
            age_threshold_days=days,
            max_buckets=settings.MAX_BUCKETS_PER_SCAN
        )
        
        if not results:
            click.echo("No old buckets found.")
            return
            
        click.echo(f"\nFound {len(results)} old buckets:")
        for bucket in results:
            click.echo(f"\nProcessing bucket: {bucket['name']}")
            if dry_run:
                click.echo(f"DRY RUN: Would delete bucket {bucket['name']}")
                continue
                
            success = deleter.delete_bucket(bucket['name'], dry_run=False)
            if success:
                click.echo(f"Successfully deleted {bucket['name']}")
            else:
                click.echo(f"Failed to delete {bucket['name']}", err=True)
                
    except Exception as e:
        click.echo(f"Error during cleanup: {str(e)}", err=True)

if __name__ == '__main__':
    cli()