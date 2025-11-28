"""
Models for the bakery ordering system.
"""

import secrets

from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class CustomUser(AbstractUser):
    """Extended user model with email verification."""

    email = models.EmailField(unique=True, verbose_name="E-Mail-Adresse")
    is_verified_email = models.BooleanField(
        default=False, verbose_name="E-Mail verifiziert"
    )
    email_verification_token = models.CharField(max_length=100, blank=True, null=True)
    email_verification_sent_at = models.DateTimeField(blank=True, null=True)

    # Customer-specific fields
    customer_number = models.CharField(
        max_length=50, blank=True, null=True, unique=True, verbose_name="Kundennummer"
    )
    delivery_fee_cents = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Lieferkosten (Cent)",
        help_text="Pauschale Lieferkosten für diesen Kunden",
    )

    # Default delivery address
    default_street = models.CharField(max_length=200, blank=True, verbose_name="Straße")
    default_city = models.CharField(max_length=100, blank=True, verbose_name="Stadt")
    default_postal_code = models.CharField(
        max_length=20, blank=True, verbose_name="PLZ"
    )
    default_phone = models.CharField(max_length=50, blank=True, verbose_name="Telefon")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        verbose_name = "Benutzer"
        verbose_name_plural = "Benutzer"

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    def generate_verification_token(self):
        """Generate a new email verification token."""
        self.email_verification_token = secrets.token_urlsafe(32)
        self.email_verification_sent_at = timezone.now()
        self.save(
            update_fields=["email_verification_token", "email_verification_sent_at"]
        )
        return self.email_verification_token

    def verify_email(self, token):
        """Verify email with the provided token."""
        if self.email_verification_token == token and not self.is_verified_email:
            self.is_verified_email = True
            self.email_verification_token = None
            self.save(update_fields=["is_verified_email", "email_verification_token"])
            return True
        return False

    @property
    def delivery_fee_euro(self):
        """Return delivery fee in Euro."""
        return self.delivery_fee_cents / 100


class Product(models.Model):
    """Product model for bakery items."""

    sku = models.CharField(max_length=50, unique=True, verbose_name="SKU")
    name = models.CharField(max_length=200, verbose_name="Name")
    description = models.TextField(blank=True, verbose_name="Beschreibung")
    price_cents = models.IntegerField(
        validators=[MinValueValidator(0)],
        verbose_name="Preis (Cent)",
        help_text="Preis in Cent (z.B. 250 für 2,50€)",
    )
    available = models.BooleanField(default=True, verbose_name="Verfügbar")
    max_per_order = models.IntegerField(
        default=99,
        validators=[MinValueValidator(1)],
        verbose_name="Max. pro Bestellung",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Erstellt am")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Aktualisiert am")

    class Meta:
        verbose_name = "Produkt"
        verbose_name_plural = "Produkte"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.sku})"

    @property
    def price_euro(self):
        """Return price in Euro."""
        return self.price_cents / 100


class Order(models.Model):
    """Order model for customer orders."""

    STATUS_CHOICES = [
        ("DRAFT", "Entwurf"),
        ("PLACED", "Aufgegeben"),
        ("EXPORTED", "Exportiert"),
        ("CANCELLED", "Storniert"),
    ]

    DELIVERY_TYPE_CHOICES = [
        ("PICKUP", "Abholung"),
        ("DELIVERY", "Lieferung"),
    ]

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="Benutzer",
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="DRAFT", verbose_name="Status"
    )
    total_cents = models.IntegerField(
        default=0, validators=[MinValueValidator(0)], verbose_name="Gesamt (Cent)"
    )
    delivery_fee_cents = models.IntegerField(
        default=0, validators=[MinValueValidator(0)], verbose_name="Lieferkosten (Cent)"
    )

    # Delivery/Pickup information
    delivery_type = models.CharField(
        max_length=20,
        choices=DELIVERY_TYPE_CHOICES,
        default="DELIVERY",
        verbose_name="Lieferart",
    )
    desired_time = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Gewünschte Uhrzeit",
        help_text="Gewünschte Abhol- oder Lieferzeit",
    )

    # Delivery address (can override user's default)
    delivery_street = models.CharField(
        max_length=200, blank=True, verbose_name="Lieferstraße"
    )
    delivery_city = models.CharField(
        max_length=100, blank=True, verbose_name="Lieferstadt"
    )
    delivery_postal_code = models.CharField(
        max_length=20, blank=True, verbose_name="Liefer-PLZ"
    )
    delivery_phone = models.CharField(
        max_length=50, blank=True, verbose_name="Liefertelefon"
    )
    delivery_notes = models.TextField(blank=True, verbose_name="Lieferhinweise")

    placed_at = models.DateTimeField(
        blank=True, null=True, verbose_name="Aufgegeben am"
    )
    exported_at = models.DateTimeField(
        blank=True, null=True, verbose_name="Exportiert am"
    )
    external_export_id = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Externe Export-ID"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Erstellt am")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Aktualisiert am")

    class Meta:
        verbose_name = "Bestellung"
        verbose_name_plural = "Bestellungen"
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"Bestellung #{self.id} - {self.user.email} ({self.get_status_display()})"
        )

    @property
    def total_euro(self):
        """Return total in Euro."""
        return self.total_cents / 100

    @property
    def grand_total_cents(self):
        """Return total including delivery fees."""
        return self.total_cents + self.delivery_fee_cents

    @property
    def grand_total_euro(self):
        """Return grand total in Euro."""
        return self.grand_total_cents / 100

    @property
    def is_editable(self):
        """Check if order can still be edited (before 22:00 on the day after placement if placed after 22:00)."""
        if self.status != "PLACED" or not self.placed_at:
            return False

        from datetime import timedelta

        now = timezone.now()

        # Determine the cutoff date based on placement time
        if self.placed_at.hour >= 22:
            # If placed after 22:00, cutoff is 22:00 on the next day
            cutoff_date = (self.placed_at + timedelta(days=1)).date()
        else:
            # If placed before 22:00, cutoff is 22:00 on the same day
            cutoff_date = self.placed_at.date()

        # Build cutoff datetime
        cutoff = timezone.datetime.combine(
            cutoff_date,
            timezone.datetime.min.time().replace(hour=22, minute=0, second=0),
        )
        cutoff = timezone.make_aware(cutoff) if timezone.is_naive(cutoff) else cutoff

        return now < cutoff

    @property
    def is_cancellable(self):
        """Same as editable - can cancel before cutoff."""
        return self.is_editable

    def calculate_total(self):
        """Calculate and update order total from items and delivery fee."""
        items_total = sum(
            item.quantity * item.unit_price_cents for item in self.items.all()
        )
        self.total_cents = items_total

        # Set delivery fee from user's default if delivery type is DELIVERY
        if self.delivery_type == "DELIVERY" and self.user:
            self.delivery_fee_cents = self.user.delivery_fee_cents
        else:
            self.delivery_fee_cents = 0

        self.save(update_fields=["total_cents", "delivery_fee_cents"])
        return self.grand_total_cents

    def place_order(self):
        """Place the order (change status from DRAFT to PLACED)."""
        if self.status != "DRAFT":
            raise ValueError(f"Order cannot be placed. Current status: {self.status}")

        if not self.items.exists():
            raise ValueError("Order has no items")

        self.calculate_total()
        self.status = "PLACED"
        self.placed_at = timezone.now()
        self.save(update_fields=["status", "placed_at"])

    def cancel_order(self):
        """Cancel the order."""
        if self.status == "EXPORTED":
            raise ValueError("Exported orders cannot be cancelled")

        self.status = "CANCELLED"
        self.save(update_fields=["status"])


class OrderItem(models.Model):
    """OrderItem model for individual products in an order."""

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items", verbose_name="Bestellung"
    )
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, verbose_name="Produkt"
    )
    quantity = models.IntegerField(
        validators=[MinValueValidator(1)], verbose_name="Menge"
    )
    unit_price_cents = models.IntegerField(
        validators=[MinValueValidator(0)],
        verbose_name="Einzelpreis (Cent)",
        help_text="Preis zum Zeitpunkt der Bestellung",
    )

    class Meta:
        verbose_name = "Bestellposition"
        verbose_name_plural = "Bestellpositionen"
        unique_together = ["order", "product"]

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    @property
    def unit_price_euro(self):
        """Return unit price in Euro."""
        return self.unit_price_cents / 100

    @property
    def subtotal_cents(self):
        """Return subtotal for this item in cents."""
        return self.quantity * self.unit_price_cents

    @property
    def subtotal_euro(self):
        """Return subtotal in Euro."""
        return self.subtotal_cents / 100

    def clean(self):
        """Validate quantity against product max_per_order."""
        from django.core.exceptions import ValidationError

        if self.quantity > self.product.max_per_order:
            raise ValidationError(
                f"Menge überschreitet Maximum von {self.product.max_per_order} für {self.product.name}"
            )

    def save(self, *args, **kwargs):
        """Save and snapshot the product price if not set."""
        if not self.unit_price_cents:
            self.unit_price_cents = self.product.price_cents
        self.full_clean()
        super().save(*args, **kwargs)


class OrderChangeRequest(models.Model):
    """Request to change or cancel an exported order."""

    REQUEST_TYPE_CHOICES = [
        ("CANCEL", "Stornierung"),
        ("MODIFY", "Änderung"),
    ]

    STATUS_CHOICES = [
        ("PENDING", "Ausstehend"),
        ("APPROVED", "Genehmigt"),
        ("REJECTED", "Abgelehnt"),
    ]

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="change_requests",
        verbose_name="Bestellung",
    )
    request_type = models.CharField(
        max_length=20, choices=REQUEST_TYPE_CHOICES, verbose_name="Anfragetyp"
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="PENDING", verbose_name="Status"
    )
    reason = models.TextField(verbose_name="Begründung")
    admin_notes = models.TextField(blank=True, verbose_name="Admin-Notizen")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Erstellt am")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Aktualisiert am")

    class Meta:
        verbose_name = "Änderungsanfrage"
        verbose_name_plural = "Änderungsanfragen"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_request_type_display()} für Bestellung #{self.order.id} - {self.get_status_display()}"


class ExportLog(models.Model):
    """Log of export operations to Access database."""

    STATUS_CHOICES = [
        ("OK", "Erfolgreich"),
        ("ERROR", "Fehler"),
    ]

    run_at = models.DateTimeField(auto_now_add=True, verbose_name="Ausgeführt am")
    orders_exported = models.IntegerField(
        default=0, verbose_name="Anzahl exportierter Bestellungen"
    )
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="OK", verbose_name="Status"
    )
    details = models.TextField(blank=True, verbose_name="Details")

    class Meta:
        verbose_name = "Export-Log"
        verbose_name_plural = "Export-Logs"
        ordering = ["-run_at"]

    def __str__(self):
        return f"Export {self.run_at.strftime('%Y-%m-%d %H:%M')} - {self.get_status_display()} ({self.orders_exported} Bestellungen)"
