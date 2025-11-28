"""
Management command to export placed orders to CSV for Access database import.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from bestellungen.models import Order, ExportLog
import csv
import os
from datetime import datetime


class Command(BaseCommand):
    help = "Export placed orders to CSV for Access database import"

    def add_arguments(self, parser):
        parser.add_argument(
            '--target',
            type=str,
            default='csv',
            help='Export target: csv (default)'
        )
        parser.add_argument(
            '--since',
            type=str,
            help='Export orders since timestamp (ISO format, optional)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simulate export without marking orders as exported'
        )

    def handle(self, *args, **options):
        target = options['target']
        since = options.get('since')
        dry_run = options.get('dry_run', False)
        
        self.stdout.write(self.style.WARNING('=' * 60))
        self.stdout.write(self.style.WARNING('  EXPORT ORDERS TO ACCESS DATABASE'))
        self.stdout.write(self.style.WARNING('=' * 60))
        
        # Query orders to export
        orders_query = Order.objects.filter(
            status='PLACED',
            exported_at__isnull=True
        ).select_related('user').prefetch_related('items__product')
        
        if since:
            try:
                since_dt = datetime.fromisoformat(since)
                orders_query = orders_query.filter(placed_at__gte=since_dt)
                self.stdout.write(f"Filtering orders since: {since_dt}")
            except ValueError:
                self.stdout.write(self.style.ERROR(f"Invalid timestamp format: {since}"))
                return
        
        orders = list(orders_query)
        
        if not orders:
            self.stdout.write(self.style.SUCCESS("✓ No orders to export"))
            return
        
        self.stdout.write(f"\nFound {len(orders)} order(s) to export:")
        for order in orders:
            self.stdout.write(f"  - Order #{order.id} ({order.user.email}) - {order.items.count()} items")
        
        # Create export directory if it doesn't exist
        export_path = getattr(settings, 'EXPORT_CSV_PATH', '/tmp/exports/')
        os.makedirs(export_path, exist_ok=True)
        
        # Generate CSV filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_filename = f'export_orders_{timestamp}.csv'
        csv_filepath = os.path.join(export_path, csv_filename)
        
        # Export to CSV
        try:
            self.export_to_csv(orders, csv_filepath)
            self.stdout.write(self.style.SUCCESS(f"\n✓ CSV exported to: {csv_filepath}"))
        except Exception as e:
            error_msg = f"Error exporting to CSV: {str(e)}"
            self.stdout.write(self.style.ERROR(f"✗ {error_msg}"))
            
            # Log error
            ExportLog.objects.create(
                orders_exported=0,
                status='ERROR',
                details=error_msg
            )
            return
        
        # Mark orders as exported (unless dry-run)
        if not dry_run:
            self.mark_orders_exported(orders)
            self.stdout.write(self.style.SUCCESS(f"✓ {len(orders)} order(s) marked as exported"))
            
            # Create success log
            ExportLog.objects.create(
                orders_exported=len(orders),
                status='OK',
                details=f"Successfully exported {len(orders)} orders to {csv_filename}"
            )
        else:
            self.stdout.write(self.style.WARNING("\n⚠ DRY RUN - Orders NOT marked as exported"))
        
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 60))
        self.stdout.write(self.style.SUCCESS('  EXPORT COMPLETED'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        # Print next steps
        self.stdout.write("\nNext steps:")
        self.stdout.write(f"1. Transfer CSV file to Windows host via VPN")
        self.stdout.write(f"2. Run: python write_to_access.py {csv_filename}")
        self.stdout.write(f"3. Verify import in Access database")
    
    def export_to_csv(self, orders, filepath):
        """Export orders to CSV file."""
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header
            writer.writerow([
                'order_id',
                'user_id',
                'user_email',
                'user_first_name',
                'user_last_name',
                'sku',
                'product_name',
                'quantity',
                'unit_price_cents',
                'placed_at',
                'order_total_cents'
            ])
            
            # Data rows
            for order in orders:
                for item in order.items.all():
                    writer.writerow([
                        order.id,
                        order.user.id,
                        order.user.email,
                        order.user.first_name,
                        order.user.last_name,
                        item.product.sku,
                        item.product.name,
                        item.quantity,
                        item.unit_price_cents,
                        order.placed_at.isoformat(),
                        order.total_cents
                    ])
        
        self.stdout.write(f"  Wrote {sum(o.items.count() for o in orders)} order items to CSV")
    
    def mark_orders_exported(self, orders):
        """Mark orders as exported."""
        with transaction.atomic():
            now = timezone.now()
            for order in orders:
                order.status = 'EXPORTED'
                order.exported_at = now
                order.save(update_fields=['status', 'exported_at'])
