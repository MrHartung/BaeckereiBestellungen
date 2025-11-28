"""
Management command to load sample data for testing.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from bestellungen.models import Product, Order, OrderItem
from django.utils import timezone

User = get_user_model()


class Command(BaseCommand):
    help = "Load sample data for testing"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Creating sample data...'))
        
        # Create sample users
        if not User.objects.filter(email='test@example.com').exists():
            user1 = User.objects.create_user(
                username='testuser',
                email='test@example.com',
                password='testpass1234',
                first_name='Max',
                last_name='Mustermann',
                is_verified_email=True
            )
            self.stdout.write(self.style.SUCCESS(f'✓ Created user: {user1.email}'))
        else:
            user1 = User.objects.get(email='test@example.com')
            self.stdout.write(f'  User already exists: {user1.email}')
        
        # Create admin user
        if not User.objects.filter(email='admin@example.com').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin1234567890',
                first_name='Admin',
                last_name='User',
                is_verified_email=True
            )
            self.stdout.write(self.style.SUCCESS(f'✓ Created admin: {admin.email}'))
        else:
            self.stdout.write('  Admin already exists')
        
        # Create sample products
        products_data = [
            {
                'sku': 'BR-001',
                'name': 'Bauernbrot',
                'description': 'Rustikales Bauernbrot aus regionalen Zutaten',
                'price_cents': 350,
                'max_per_order': 5
            },
            {
                'sku': 'BR-002',
                'name': 'Vollkornbrot',
                'description': 'Gesundes Vollkornbrot mit Sonnenblumenkernen',
                'price_cents': 420,
                'max_per_order': 5
            },
            {
                'sku': 'BR-003',
                'name': 'Baguette',
                'description': 'Französisches Baguette, knusprig und frisch',
                'price_cents': 180,
                'max_per_order': 10
            },
            {
                'sku': 'BR-004',
                'name': 'Brezel',
                'description': 'Klassische Laugenbrezel',
                'price_cents': 90,
                'max_per_order': 20
            },
            {
                'sku': 'CK-001',
                'name': 'Schokoladenkuchen',
                'description': 'Saftiger Schokoladenkuchen',
                'price_cents': 1250,
                'max_per_order': 2
            },
            {
                'sku': 'CK-002',
                'name': 'Apfelkuchen',
                'description': 'Hausgemachter Apfelkuchen mit Zimt',
                'price_cents': 1150,
                'max_per_order': 2
            },
            {
                'sku': 'SN-001',
                'name': 'Croissant',
                'description': 'Butteriges französisches Croissant',
                'price_cents': 150,
                'max_per_order': 15
            },
            {
                'sku': 'SN-002',
                'name': 'Berliner',
                'description': 'Berliner mit Marmeladenfüllung',
                'price_cents': 120,
                'max_per_order': 20
            },
        ]
        
        created_products = []
        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                sku=product_data['sku'],
                defaults=product_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created product: {product.name}'))
            else:
                self.stdout.write(f'  Product already exists: {product.name}')
            created_products.append(product)
        
        # Create sample orders
        if not Order.objects.filter(user=user1, status='PLACED').exists():
            # Order 1 - Placed
            order1 = Order.objects.create(user=user1, status='DRAFT')
            OrderItem.objects.create(
                order=order1,
                product=created_products[0],  # Bauernbrot
                quantity=2,
                unit_price_cents=created_products[0].price_cents
            )
            OrderItem.objects.create(
                order=order1,
                product=created_products[3],  # Brezel
                quantity=5,
                unit_price_cents=created_products[3].price_cents
            )
            order1.place_order()
            self.stdout.write(self.style.SUCCESS(f'✓ Created sample order #{order1.id}'))
            
            # Order 2 - Draft (in cart)
            order2 = Order.objects.create(user=user1, status='DRAFT')
            OrderItem.objects.create(
                order=order2,
                product=created_products[6],  # Croissant
                quantity=3,
                unit_price_cents=created_products[6].price_cents
            )
            order2.calculate_total()
            self.stdout.write(self.style.SUCCESS(f'✓ Created draft order #{order2.id}'))
        else:
            self.stdout.write('  Sample orders already exist')
        
        self.stdout.write(self.style.SUCCESS('\n✓ Sample data creation completed!'))
        self.stdout.write('\nLogin credentials:')
        self.stdout.write('  User: test@example.com / testpass1234')
        self.stdout.write('  Admin: admin@example.com / admin1234567890')
