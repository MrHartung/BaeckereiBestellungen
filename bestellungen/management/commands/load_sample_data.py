"""
Management command to load sample data for testing.
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from bestellungen.models import Order, OrderItem, Product

User = get_user_model()


class Command(BaseCommand):
    help = "Load sample data for testing"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Creating sample data..."))

        # Create sample users
        if not User.objects.filter(email="test@example.com").exists():
            user1 = User.objects.create_user(
                username="testuser",
                email="test@example.com",
                password="testpass1234",
                first_name="Max",
                last_name="Mustermann",
                is_verified_email=True,
            )
            self.stdout.write(self.style.SUCCESS(f"✓ Created user: {user1.email}"))
        else:
            user1 = User.objects.get(email="test@example.com")
            self.stdout.write(f"  User already exists: {user1.email}")

        # Create admin user
        if not User.objects.filter(email="admin@example.com").exists():
            admin = User.objects.create_superuser(
                username="admin",
                email="admin@example.com",
                password="admin1234567890",
                first_name="Admin",
                last_name="User",
                is_verified_email=True,
            )
            self.stdout.write(self.style.SUCCESS(f"✓ Created admin: {admin.email}"))
        else:
            self.stdout.write("  Admin already exists")

        # Create sample products (Italienische Bäckerei)
        products_data = [
            # 1kg Brote
            {
                "sku": "1000",
                "name": "Pane pugliese lang",
                "description": "1kg",
                "price_cents": 450,
                "max_per_order": 999,
            },
            {
                "sku": "1001",
                "name": "Pane pugliese rund",
                "description": "1kg",
                "price_cents": 450,
                "max_per_order": 999,
            },
            {
                "sku": "1002",
                "name": "Pizzaterra",
                "description": "1kg",
                "price_cents": 420,
                "max_per_order": 999,
            },
            {
                "sku": "1003",
                "name": "Bazzuca",
                "description": "1kg",
                "price_cents": 480,
                "max_per_order": 999,
            },
            {
                "sku": "1004",
                "name": "Ciambella",
                "description": "1kg",
                "price_cents": 460,
                "max_per_order": 999,
            },
            {
                "sku": "1005",
                "name": "Pane speciale lang",
                "description": "1kg",
                "price_cents": 490,
                "max_per_order": 999,
            },
            {
                "sku": "1009",
                "name": "Focaccia Rosmarino",
                "description": "1kg",
                "price_cents": 520,
                "max_per_order": 999,
            },
            # 500g Brote
            {
                "sku": "1100",
                "name": "Pane pugliese lang",
                "description": "500g",
                "price_cents": 240,
                "max_per_order": 999,
            },
            {
                "sku": "1101",
                "name": "Pane pugliese rund",
                "description": "500g",
                "price_cents": 240,
                "max_per_order": 999,
            },
            {
                "sku": "1102",
                "name": "Pizzaterra",
                "description": "500g",
                "price_cents": 220,
                "max_per_order": 999,
            },
            {
                "sku": "1103",
                "name": "Ciambella",
                "description": "500g",
                "price_cents": 240,
                "max_per_order": 999,
            },
            {
                "sku": "1104",
                "name": "Pane speciale lang",
                "description": "500g",
                "price_cents": 260,
                "max_per_order": 999,
            },
            {
                "sku": "1107",
                "name": "Mezza Luna Spec.",
                "description": "500g",
                "price_cents": 270,
                "max_per_order": 999,
            },
            {
                "sku": "1108",
                "name": "Pane Sesam lang",
                "description": "500g",
                "price_cents": 270,
                "max_per_order": 999,
            },
            {
                "sku": "1109",
                "name": "Bazzuca",
                "description": "500g",
                "price_cents": 250,
                "max_per_order": 999,
            },
            {
                "sku": "1110",
                "name": "Licata",
                "description": "500g",
                "price_cents": 260,
                "max_per_order": 999,
            },
            {
                "sku": "1111",
                "name": "Fladenbrot",
                "description": "500g",
                "price_cents": 230,
                "max_per_order": 999,
            },
            {
                "sku": "1112",
                "name": "Pariserbrot",
                "description": "500g",
                "price_cents": 240,
                "max_per_order": 999,
            },
            {
                "sku": "1113",
                "name": "Focaccia origano",
                "description": "500g",
                "price_cents": 270,
                "max_per_order": 999,
            },
            {
                "sku": "1115",
                "name": "Ciambella di semola",
                "description": "500g",
                "price_cents": 260,
                "max_per_order": 999,
            },
            {
                "sku": "1122",
                "name": "Il Siciliano mit sesam",
                "description": "500g",
                "price_cents": 280,
                "max_per_order": 999,
            },
            # 250g Spezialbrote
            {
                "sku": "2000",
                "name": "Olivenbrot rund",
                "description": "250g",
                "price_cents": 180,
                "max_per_order": 999,
            },
            {
                "sku": "2001",
                "name": "Olivenbrot lang",
                "description": "250g",
                "price_cents": 180,
                "max_per_order": 999,
            },
            {
                "sku": "2002",
                "name": "Ciabattabrot",
                "description": "250g",
                "price_cents": 170,
                "max_per_order": 999,
            },
            {
                "sku": "2003",
                "name": "Oreganobrot",
                "description": "250g",
                "price_cents": 170,
                "max_per_order": 999,
            },
            {
                "sku": "2004",
                "name": "Zwiebelbrot",
                "description": "250g",
                "price_cents": 170,
                "max_per_order": 999,
            },
            {
                "sku": "2005",
                "name": "Knoblauchbrot",
                "description": "250g",
                "price_cents": 180,
                "max_per_order": 999,
            },
            {
                "sku": "2006",
                "name": "Tomatenbrot",
                "description": "250g",
                "price_cents": 180,
                "max_per_order": 999,
            },
            {
                "sku": "2007",
                "name": "Oliven oregano",
                "description": "250g",
                "price_cents": 190,
                "max_per_order": 999,
            },
            {
                "sku": "2008",
                "name": "Paprikabrot",
                "description": "250g",
                "price_cents": 180,
                "max_per_order": 999,
            },
            {
                "sku": "2009",
                "name": "Rosmarinobrot",
                "description": "250g",
                "price_cents": 180,
                "max_per_order": 999,
            },
            # 200g Crostoni
            {
                "sku": "2012",
                "name": "Focaccia olive orig",
                "description": "200g",
                "price_cents": 190,
                "max_per_order": 999,
            },
            {
                "sku": "2013",
                "name": "Crostoni baresi",
                "description": "200g",
                "price_cents": 160,
                "max_per_order": 999,
            },
            {
                "sku": "2014",
                "name": "Crostoni olive",
                "description": "200g",
                "price_cents": 170,
                "max_per_order": 999,
            },
            {
                "sku": "2016",
                "name": "Crostoni origano",
                "description": "200g",
                "price_cents": 160,
                "max_per_order": 999,
            },
            {
                "sku": "2017",
                "name": "Crostoni integrali",
                "description": "200g",
                "price_cents": 170,
                "max_per_order": 999,
            },
            {
                "sku": "2018",
                "name": "Crostoni aglio",
                "description": "200g",
                "price_cents": 170,
                "max_per_order": 999,
            },
            {
                "sku": "2019",
                "name": "Crostoni peperoncino",
                "description": "200g",
                "price_cents": 170,
                "max_per_order": 999,
            },
            # Brötchen & Panini
            {
                "sku": "3000",
                "name": "Panini pugliese",
                "description": "100g",
                "price_cents": 70,
                "max_per_order": 999,
            },
            {
                "sku": "3001",
                "name": "Panini Italiani",
                "description": "100g",
                "price_cents": 70,
                "max_per_order": 999,
            },
            {
                "sku": "3002",
                "name": "Rosette",
                "description": "100g",
                "price_cents": 75,
                "max_per_order": 999,
            },
            {
                "sku": "3003",
                "name": "Fladenbrötchen",
                "description": "100g",
                "price_cents": 70,
                "max_per_order": 999,
            },
            {
                "sku": "3004",
                "name": "Cocktailbrötchen",
                "description": "30g",
                "price_cents": 30,
                "max_per_order": 999,
            },
            {
                "sku": "3005",
                "name": "Bagels",
                "description": "100g",
                "price_cents": 80,
                "max_per_order": 999,
            },
            {
                "sku": "3006",
                "name": "Bagels mit sesam",
                "description": "100g",
                "price_cents": 85,
                "max_per_order": 999,
            },
            {
                "sku": "3008",
                "name": "Sesambrötchen",
                "description": "100g",
                "price_cents": 75,
                "max_per_order": 999,
            },
            {
                "sku": "3009",
                "name": "Partybrötchen mix",
                "description": "30g",
                "price_cents": 35,
                "max_per_order": 999,
            },
            {
                "sku": "3010",
                "name": "Focaccine",
                "description": "100g",
                "price_cents": 80,
                "max_per_order": 999,
            },
            {
                "sku": "3011",
                "name": "Panini integrali",
                "description": "100g",
                "price_cents": 75,
                "max_per_order": 999,
            },
            {
                "sku": "3020",
                "name": "Panino rotondo semola",
                "description": "125g",
                "price_cents": 90,
                "max_per_order": 999,
            },
            {
                "sku": "3030",
                "name": "Panino lungo semola",
                "description": "125g",
                "price_cents": 90,
                "max_per_order": 999,
            },
            {
                "sku": "3040",
                "name": "Panino lungo origano",
                "description": "125g",
                "price_cents": 95,
                "max_per_order": 999,
            },
            {
                "sku": "3050",
                "name": "Ciabattino bianco",
                "description": "125g",
                "price_cents": 90,
                "max_per_order": 999,
            },
            {
                "sku": "3060",
                "name": "Focaccine origano",
                "description": "125g",
                "price_cents": 95,
                "max_per_order": 999,
            },
            # Gebäck
            {
                "sku": "4000",
                "name": "Cornetti",
                "description": "Stück",
                "price_cents": 140,
                "max_per_order": 999,
            },
            {
                "sku": "4001",
                "name": "Cornetti crema",
                "description": "Stück",
                "price_cents": 160,
                "max_per_order": 999,
            },
            {
                "sku": "4002",
                "name": "Cornetti cioccolata",
                "description": "Stück",
                "price_cents": 160,
                "max_per_order": 999,
            },
            {
                "sku": "4003",
                "name": "Taralli",
                "description": "1 Pckg",
                "price_cents": 350,
                "max_per_order": 999,
            },
            {
                "sku": "4004",
                "name": "Grissini",
                "description": "1 Pckg",
                "price_cents": 320,
                "max_per_order": 999,
            },
            {
                "sku": "4005",
                "name": "Cantucci",
                "description": "1 Pckg",
                "price_cents": 420,
                "max_per_order": 999,
            },
            # Pizza & Pizzetta
            {
                "sku": "5000",
                "name": "Pizzetta pomodoro",
                "description": "Stück",
                "price_cents": 180,
                "max_per_order": 999,
            },
            {
                "sku": "5001",
                "name": "Pizzetta paprika",
                "description": "Stück",
                "price_cents": 190,
                "max_per_order": 999,
            },
            {
                "sku": "5002",
                "name": "Pizza pomodoro",
                "description": "40x50cm",
                "price_cents": 850,
                "max_per_order": 999,
            },
            {
                "sku": "5003",
                "name": "Pizza paprika",
                "description": "40x50cm",
                "price_cents": 900,
                "max_per_order": 999,
            },
            {
                "sku": "5005",
                "name": "Mini origano",
                "description": "100g",
                "price_cents": 90,
                "max_per_order": 999,
            },
            {
                "sku": "5006",
                "name": "Mini pomodoro",
                "description": "100g",
                "price_cents": 95,
                "max_per_order": 999,
            },
            {
                "sku": "5007",
                "name": "Mini cipolla",
                "description": "100g",
                "price_cents": 95,
                "max_per_order": 999,
            },
            {
                "sku": "5008",
                "name": "Pizza bianca",
                "description": "40x50cm",
                "price_cents": 800,
                "max_per_order": 999,
            },
            {
                "sku": "5009",
                "name": "Pizzetta bianca",
                "description": "Stück",
                "price_cents": 170,
                "max_per_order": 999,
            },
            # Rusticelle
            {
                "sku": "5010",
                "name": "Rusticelle Salami",
                "description": "Stück",
                "price_cents": 220,
                "max_per_order": 999,
            },
            {
                "sku": "5020",
                "name": "Rusticelle Tonno",
                "description": "Stück",
                "price_cents": 240,
                "max_per_order": 999,
            },
            {
                "sku": "5040",
                "name": "Rusticelle Spinat",
                "description": "Stück",
                "price_cents": 220,
                "max_per_order": 999,
            },
            {
                "sku": "5050",
                "name": "Rusticelle Prosciutto",
                "description": "Stück",
                "price_cents": 240,
                "max_per_order": 999,
            },
            {
                "sku": "5100",
                "name": "Friselle",
                "description": "1 Pckg",
                "price_cents": 380,
                "max_per_order": 999,
            },
            # Pane di semola
            {
                "sku": "6000",
                "name": "Pane di semola L.",
                "description": "750g",
                "price_cents": 320,
                "max_per_order": 999,
            },
            {
                "sku": "6001",
                "name": "Pane di semola R.",
                "description": "750g",
                "price_cents": 320,
                "max_per_order": 999,
            },
            {
                "sku": "6002",
                "name": "Pane di semola L.",
                "description": "5kg",
                "price_cents": 2000,
                "max_per_order": 999,
            },
            {
                "sku": "6003",
                "name": "Ciabatta di semola",
                "description": "250g",
                "price_cents": 180,
                "max_per_order": 999,
            },
            {
                "sku": "6004",
                "name": "Panini di semola",
                "description": "100g",
                "price_cents": 75,
                "max_per_order": 999,
            },
            {
                "sku": "6006",
                "name": "Pane di semola L.",
                "description": "2kg",
                "price_cents": 850,
                "max_per_order": 999,
            },
            {
                "sku": "6011",
                "name": "Pane di semola L.",
                "description": "10kg",
                "price_cents": 3900,
                "max_per_order": 999,
            },
            {
                "sku": "6012",
                "name": "Bazzuca di semola",
                "description": "500g",
                "price_cents": 260,
                "max_per_order": 999,
            },
            {
                "sku": "6018",
                "name": "Pane di semola L.",
                "description": "3kg",
                "price_cents": 1250,
                "max_per_order": 999,
            },
            # Panini quadrati
            {
                "sku": "6104",
                "name": "Panini quadrati",
                "description": "100g",
                "price_cents": 80,
                "max_per_order": 999,
            },
            {
                "sku": "6105",
                "name": "Quadrati Tomate",
                "description": "100g",
                "price_cents": 85,
                "max_per_order": 999,
            },
            {
                "sku": "6106",
                "name": "Quadrati Oliven",
                "description": "100g",
                "price_cents": 90,
                "max_per_order": 999,
            },
            {
                "sku": "6107",
                "name": "Quadrati Zwiebel",
                "description": "100g",
                "price_cents": 85,
                "max_per_order": 999,
            },
            {
                "sku": "6108",
                "name": "Quadrati Aubergine",
                "description": "100g",
                "price_cents": 90,
                "max_per_order": 999,
            },
            {
                "sku": "6109",
                "name": "Quadrati Paprika",
                "description": "100g",
                "price_cents": 85,
                "max_per_order": 999,
            },
            {
                "sku": "6125",
                "name": "Bazzuca di semola",
                "description": "5kg",
                "price_cents": 2100,
                "max_per_order": 999,
            },
            {
                "sku": "6129",
                "name": "Pane di semola",
                "description": "20kg",
                "price_cents": 7500,
                "max_per_order": 999,
            },
            # Spezialbrote
            {
                "sku": "6202",
                "name": "Alexanderlaible",
                "description": "750g",
                "price_cents": 380,
                "max_per_order": 999,
            },
            {
                "sku": "6203",
                "name": "Roggolino (Roggen)",
                "description": "750g",
                "price_cents": 380,
                "max_per_order": 999,
            },
            {
                "sku": "6206",
                "name": "Roggolino (Roggen)",
                "description": "3kg",
                "price_cents": 1450,
                "max_per_order": 999,
            },
            {
                "sku": "6219",
                "name": "Alexanderlaible",
                "description": "3kg",
                "price_cents": 1450,
                "max_per_order": 999,
            },
            {
                "sku": "6221",
                "name": "Alexanderlaible",
                "description": "2kg",
                "price_cents": 980,
                "max_per_order": 999,
            },
            {
                "sku": "6299",
                "name": "Alexanderlaible",
                "description": "5kg",
                "price_cents": 2300,
                "max_per_order": 999,
            },
            # Pane contadino
            {
                "sku": "7000",
                "name": "Pane contadino L",
                "description": "2kg",
                "price_cents": 920,
                "max_per_order": 999,
            },
            {
                "sku": "7001",
                "name": "Pane contadino R",
                "description": "2kg",
                "price_cents": 920,
                "max_per_order": 999,
            },
            {
                "sku": "7002",
                "name": "Pane contadino L",
                "description": "3kg",
                "price_cents": 1350,
                "max_per_order": 999,
            },
            {
                "sku": "7003",
                "name": "Pane contadino R",
                "description": "3kg",
                "price_cents": 1350,
                "max_per_order": 999,
            },
            {
                "sku": "7004",
                "name": "Pane contadino L",
                "description": "5kg",
                "price_cents": 2200,
                "max_per_order": 999,
            },
            {
                "sku": "7006",
                "name": "Pane contadino",
                "description": "10kg",
                "price_cents": 4300,
                "max_per_order": 999,
            },
            {
                "sku": "7007",
                "name": "Pane contadino",
                "description": "15kg",
                "price_cents": 6300,
                "max_per_order": 999,
            },
            {
                "sku": "7009",
                "name": "Pane contadino C",
                "description": "5kg",
                "price_cents": 2200,
                "max_per_order": 999,
            },
            {
                "sku": "7025",
                "name": "Bazzuca contadino",
                "description": "5kg",
                "price_cents": 2300,
                "max_per_order": 999,
            },
            # Pane Sardo
            {
                "sku": "8100",
                "name": "Pane Sardo",
                "description": "750g",
                "price_cents": 390,
                "max_per_order": 999,
            },
            # Zusatzartikel
            {
                "sku": "9001",
                "name": "Papiertüte klein",
                "description": "Für Brötchen",
                "price_cents": 10,
                "max_per_order": 999,
            },
            {
                "sku": "9002",
                "name": "Papiertüte groß",
                "description": "Für Brote",
                "price_cents": 20,
                "max_per_order": 999,
            },
            {
                "sku": "9003",
                "name": "Stoffbeutel",
                "description": "Wiederverwendbar",
                "price_cents": 250,
                "max_per_order": 999,
            },
            {
                "sku": "9010",
                "name": "Paniermehl",
                "description": "500g",
                "price_cents": 180,
                "max_per_order": 999,
            },
            {
                "sku": "9011",
                "name": "Semmelbrösel",
                "description": "500g",
                "price_cents": 180,
                "max_per_order": 999,
            },
        ]

        created_products = []
        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                sku=product_data["sku"], defaults=product_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Created product: {product.name}")
                )
            else:
                self.stdout.write(f"  Product already exists: {product.name}")
            created_products.append(product)

        # Create sample orders
        if not Order.objects.filter(user=user1, status="PLACED").exists():
            # Order 1 - Placed
            order1 = Order.objects.create(user=user1, status="DRAFT")
            OrderItem.objects.create(
                order=order1,
                product=created_products[0],  # Bauernbrot
                quantity=2,
                unit_price_cents=created_products[0].price_cents,
            )
            OrderItem.objects.create(
                order=order1,
                product=created_products[3],  # Brezel
                quantity=5,
                unit_price_cents=created_products[3].price_cents,
            )
            order1.place_order()
            self.stdout.write(
                self.style.SUCCESS(f"✓ Created sample order #{order1.id}")
            )

            # Order 2 - Draft (in cart)
            order2 = Order.objects.create(user=user1, status="DRAFT")
            OrderItem.objects.create(
                order=order2,
                product=created_products[6],  # Croissant
                quantity=3,
                unit_price_cents=created_products[6].price_cents,
            )
            order2.calculate_total()
            self.stdout.write(self.style.SUCCESS(f"✓ Created draft order #{order2.id}"))
        else:
            self.stdout.write("  Sample orders already exist")

        self.stdout.write(self.style.SUCCESS("\n✓ Sample data creation completed!"))
        self.stdout.write("\nLogin credentials:")
        self.stdout.write("  User: test@example.com / testpass1234")
        self.stdout.write("  Admin: admin@example.com / admin1234567890")
