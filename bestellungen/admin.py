"""
Admin configuration for bestellungen app.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, ExportLog, Order, OrderChangeRequest, OrderItem, Product


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Admin for CustomUser model."""

    list_display = [
        "email",
        "username",
        "first_name",
        "last_name",
        "is_verified_email",
        "is_staff",
    ]
    list_filter = ["is_verified_email", "is_staff", "is_superuser", "is_active"]
    search_fields = ["email", "username", "first_name", "last_name"]
    ordering = ["-date_joined"]

    fieldsets = UserAdmin.fieldsets + (
        (
            "E-Mail Verifikation",
            {
                "fields": (
                    "is_verified_email",
                    "email_verification_token",
                    "email_verification_sent_at",
                ),
            },
        ),
        (
            "Kundendaten",
            {
                "fields": ("customer_number", "delivery_fee_cents"),
            },
        ),
        (
            "Standard-Lieferadresse",
            {
                "fields": (
                    "default_street",
                    "default_city",
                    "default_postal_code",
                    "default_phone",
                ),
            },
        ),
    )

    readonly_fields = ["date_joined", "last_login", "email_verification_sent_at"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin for Product model."""

    list_display = [
        "sku",
        "name",
        "price_euro",
        "available",
        "max_per_order",
        "created_at",
    ]
    list_filter = ["available", "created_at"]
    search_fields = ["sku", "name", "description"]
    ordering = ["name"]

    fieldsets = [
        ("Grundinformationen", {"fields": ("sku", "name", "description")}),
        (
            "Preis & Verfügbarkeit",
            {"fields": ("price_cents", "available", "max_per_order")},
        ),
        (
            "Zeitstempel",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    ]

    readonly_fields = ["created_at", "updated_at"]

    def price_euro(self, obj):
        """Display price in Euro."""
        return f"{obj.price_euro:.2f}€"

    price_euro.short_description = "Preis"


class OrderItemInline(admin.TabularInline):
    """Inline admin for OrderItem."""

    model = OrderItem
    extra = 0
    readonly_fields = ["subtotal_euro"]

    def subtotal_euro(self, obj):
        """Display subtotal in Euro."""
        return f"{obj.subtotal_euro:.2f}€"

    subtotal_euro.short_description = "Zwischensumme"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin for Order model."""

    list_display = [
        "id",
        "user",
        "status",
        "delivery_type",
        "grand_total_euro",
        "placed_at",
        "exported_at",
    ]
    list_filter = ["status", "delivery_type", "placed_at", "exported_at"]
    search_fields = ["id", "user__email", "user__first_name", "user__last_name"]
    ordering = ["-created_at"]
    inlines = [OrderItemInline]

    fieldsets = [
        (
            "Bestellung",
            {"fields": ("user", "status", "total_cents", "delivery_fee_cents")},
        ),
        (
            "Lieferung/Abholung",
            {
                "fields": (
                    "delivery_type",
                    "desired_time",
                    "delivery_street",
                    "delivery_city",
                    "delivery_postal_code",
                    "delivery_phone",
                    "delivery_notes",
                )
            },
        ),
        (
            "Zeitstempel",
            {"fields": ("placed_at", "exported_at", "created_at", "updated_at")},
        ),
        ("Export", {"fields": ("external_export_id",), "classes": ("collapse",)}),
    ]

    readonly_fields = ["created_at", "updated_at", "total_cents", "delivery_fee_cents"]

    def total_euro(self, obj):
        """Display total in Euro."""
        return f"{obj.total_euro:.2f}€"

    total_euro.short_description = "Gesamt"

    def grand_total_euro(self, obj):
        """Display grand total with delivery in Euro."""
        return f"{obj.grand_total_euro:.2f}€"

    grand_total_euro.short_description = "Gesamt inkl. Lieferung"

    actions = ["recalculate_totals"]

    def recalculate_totals(self, request, queryset):
        """Admin action to recalculate order totals."""
        for order in queryset:
            order.calculate_total()
        self.message_user(
            request, f"{queryset.count()} Bestellungen wurden neuberechnet."
        )

    recalculate_totals.short_description = "Gesamt neu berechnen"


@admin.register(OrderChangeRequest)
class OrderChangeRequestAdmin(admin.ModelAdmin):
    """Admin for OrderChangeRequest model."""

    list_display = ["id", "order", "request_type", "status", "created_at"]
    list_filter = ["request_type", "status", "created_at"]
    search_fields = ["order__id", "order__user__email", "reason"]
    ordering = ["-created_at"]

    fieldsets = [
        ("Anfrage", {"fields": ("order", "request_type", "status", "reason")}),
        ("Admin", {"fields": ("admin_notes",)}),
        ("Zeitstempel", {"fields": ("created_at", "updated_at")}),
    ]

    readonly_fields = ["created_at", "updated_at"]


@admin.register(ExportLog)
class ExportLogAdmin(admin.ModelAdmin):
    """Admin for ExportLog model."""

    list_display = ["run_at", "status", "orders_exported", "short_details"]
    list_filter = ["status", "run_at"]
    ordering = ["-run_at"]

    fieldsets = [
        ("Export-Info", {"fields": ("run_at", "status", "orders_exported")}),
        ("Details", {"fields": ("details",)}),
    ]

    readonly_fields = ["run_at"]

    def short_details(self, obj):
        """Display shortened details."""
        if obj.details:
            return obj.details[:100] + ("..." if len(obj.details) > 100 else "")
        return "-"

    short_details.short_description = "Details (gekürzt)"

    def has_add_permission(self, request):
        """Prevent manual creation of export logs."""
        return False
