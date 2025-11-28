# Generated manually for GitHub Actions compatibility

from django.conf import settings
from django.db import migrations, models
import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="CustomUser",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        error_messages={
                            "unique": "A user with that username already exists."
                        },
                        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        max_length=150,
                        unique=True,
                        validators=[
                            django.contrib.auth.validators.UnicodeUsernameValidator()
                        ],
                        verbose_name="username",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="first name"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="last name"
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        max_length=254, unique=True, verbose_name="E-Mail-Adresse"
                    ),
                ),
                (
                    "is_verified_email",
                    models.BooleanField(
                        default=False, verbose_name="E-Mail verifiziert"
                    ),
                ),
                (
                    "email_verification_token",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                (
                    "email_verification_sent_at",
                    models.DateTimeField(blank=True, null=True),
                ),
                (
                    "customer_number",
                    models.CharField(
                        blank=True,
                        max_length=50,
                        null=True,
                        unique=True,
                        verbose_name="Kundennummer",
                    ),
                ),
                (
                    "delivery_fee_cents",
                    models.IntegerField(
                        default=0,
                        help_text="Pauschale Lieferkosten für diesen Kunden",
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="Lieferkosten (Cent)",
                    ),
                ),
                (
                    "default_street",
                    models.CharField(blank=True, max_length=200, verbose_name="Straße"),
                ),
                (
                    "default_city",
                    models.CharField(blank=True, max_length=100, verbose_name="Stadt"),
                ),
                (
                    "default_postal_code",
                    models.CharField(blank=True, max_length=20, verbose_name="PLZ"),
                ),
                (
                    "default_phone",
                    models.CharField(blank=True, max_length=50, verbose_name="Telefon"),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name": "Benutzer",
                "verbose_name_plural": "Benutzer",
            },
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="Product",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "sku",
                    models.CharField(max_length=50, unique=True, verbose_name="SKU"),
                ),
                ("name", models.CharField(max_length=200, verbose_name="Name")),
                (
                    "description",
                    models.TextField(blank=True, verbose_name="Beschreibung"),
                ),
                (
                    "price_cents",
                    models.IntegerField(
                        help_text="Preis in Cent (z.B. 250 für 2,50€)",
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="Preis (Cent)",
                    ),
                ),
                (
                    "available",
                    models.BooleanField(default=True, verbose_name="Verfügbar"),
                ),
                (
                    "max_per_order",
                    models.IntegerField(
                        default=99,
                        validators=[django.core.validators.MinValueValidator(1)],
                        verbose_name="Max. pro Bestellung",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Erstellt am"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Aktualisiert am"),
                ),
            ],
            options={
                "verbose_name": "Produkt",
                "verbose_name_plural": "Produkte",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Order",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("DRAFT", "Entwurf"),
                            ("PLACED", "Aufgegeben"),
                            ("EXPORTED", "Exportiert"),
                            ("CANCELLED", "Storniert"),
                        ],
                        default="DRAFT",
                        max_length=20,
                        verbose_name="Status",
                    ),
                ),
                (
                    "total_cents",
                    models.IntegerField(
                        default=0,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="Gesamt (Cent)",
                    ),
                ),
                (
                    "delivery_fee_cents",
                    models.IntegerField(
                        default=0,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="Lieferkosten (Cent)",
                    ),
                ),
                (
                    "delivery_type",
                    models.CharField(
                        choices=[("PICKUP", "Abholung"), ("DELIVERY", "Lieferung")],
                        default="DELIVERY",
                        max_length=20,
                        verbose_name="Lieferart",
                    ),
                ),
                (
                    "desired_time",
                    models.DateTimeField(
                        blank=True,
                        help_text="Gewünschte Abhol- oder Lieferzeit",
                        null=True,
                        verbose_name="Gewünschte Uhrzeit",
                    ),
                ),
                (
                    "delivery_street",
                    models.CharField(
                        blank=True, max_length=200, verbose_name="Lieferstraße"
                    ),
                ),
                (
                    "delivery_city",
                    models.CharField(
                        blank=True, max_length=100, verbose_name="Lieferstadt"
                    ),
                ),
                (
                    "delivery_postal_code",
                    models.CharField(
                        blank=True, max_length=20, verbose_name="Liefer-PLZ"
                    ),
                ),
                (
                    "delivery_phone",
                    models.CharField(
                        blank=True, max_length=50, verbose_name="Liefertelefon"
                    ),
                ),
                (
                    "delivery_notes",
                    models.TextField(blank=True, verbose_name="Lieferhinweise"),
                ),
                (
                    "placed_at",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Aufgegeben am"
                    ),
                ),
                (
                    "exported_at",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Exportiert am"
                    ),
                ),
                (
                    "external_export_id",
                    models.CharField(
                        blank=True,
                        max_length=100,
                        null=True,
                        verbose_name="Externe Export-ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Erstellt am"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Aktualisiert am"),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="orders",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Benutzer",
                    ),
                ),
            ],
            options={
                "verbose_name": "Bestellung",
                "verbose_name_plural": "Bestellungen",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="OrderItem",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "quantity",
                    models.IntegerField(
                        validators=[django.core.validators.MinValueValidator(1)],
                        verbose_name="Menge",
                    ),
                ),
                (
                    "unit_price_cents",
                    models.IntegerField(
                        help_text="Preis zum Zeitpunkt der Bestellung",
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="Einzelpreis (Cent)",
                    ),
                ),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="items",
                        to="bestellungen.order",
                        verbose_name="Bestellung",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="bestellungen.product",
                        verbose_name="Produkt",
                    ),
                ),
            ],
            options={
                "verbose_name": "Bestellposition",
                "verbose_name_plural": "Bestellpositionen",
                "unique_together": {("order", "product")},
            },
        ),
        migrations.CreateModel(
            name="OrderChangeRequest",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "request_type",
                    models.CharField(
                        choices=[("CANCEL", "Stornierung"), ("MODIFY", "Änderung")],
                        max_length=20,
                        verbose_name="Anfragetyp",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PENDING", "Ausstehend"),
                            ("APPROVED", "Genehmigt"),
                            ("REJECTED", "Abgelehnt"),
                        ],
                        default="PENDING",
                        max_length=20,
                        verbose_name="Status",
                    ),
                ),
                ("reason", models.TextField(verbose_name="Begründung")),
                (
                    "admin_notes",
                    models.TextField(blank=True, verbose_name="Admin-Notizen"),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Erstellt am"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Aktualisiert am"),
                ),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="change_requests",
                        to="bestellungen.order",
                        verbose_name="Bestellung",
                    ),
                ),
            ],
            options={
                "verbose_name": "Änderungsanfrage",
                "verbose_name_plural": "Änderungsanfragen",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="ExportLog",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "run_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Ausgeführt am"
                    ),
                ),
                (
                    "orders_exported",
                    models.IntegerField(
                        default=0, verbose_name="Anzahl exportierter Bestellungen"
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("OK", "Erfolgreich"), ("ERROR", "Fehler")],
                        default="OK",
                        max_length=10,
                        verbose_name="Status",
                    ),
                ),
                ("details", models.TextField(blank=True, verbose_name="Details")),
            ],
            options={
                "verbose_name": "Export-Log",
                "verbose_name_plural": "Export-Logs",
                "ordering": ["-run_at"],
            },
        ),
    ]
