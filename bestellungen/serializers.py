"""
Serializers for the bestellungen API.
"""

from django.conf import settings
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from rest_framework import serializers

from .models import CustomUser, ExportLog, Order, OrderItem, Product


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""

    password = serializers.CharField(write_only=True, min_length=10)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "email",
            "username",
            "first_name",
            "last_name",
            "password",
            "password_confirm",
        ]

    def validate(self, data):
        """Validate password confirmation."""
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError(
                {"password": "Passwörter stimmen nicht überein."}
            )
        return data

    def create(self, validated_data):
        """Create user and send verification email."""
        validated_data.pop("password_confirm")
        user = CustomUser.objects.create_user(
            email=validated_data["email"],
            username=validated_data["username"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            password=validated_data["password"],
        )

        # Generate verification token and send email
        token = user.generate_verification_token()
        self.send_verification_email(user, token)

        return user

    def send_verification_email(self, user, token):
        """Send verification email to user."""
        verification_url = f"{settings.ALLOWED_HOSTS[0]}/verify-email/{token}/"
        message = f"""
        Hallo {user.first_name},
        
        bitte verifizieren Sie Ihre E-Mail-Adresse, indem Sie auf folgenden Link klicken:
        {verification_url}
        
        Falls Sie sich nicht registriert haben, ignorieren Sie diese E-Mail.
        
        Mit freundlichen Grüßen
        Ihr Bäckerei-Team
        """

        send_mail(
            "E-Mail-Adresse bestätigen",
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user information."""

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_verified_email",
        ]
        read_only_fields = ["id", "is_verified_email"]


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """Validate credentials and check email verification."""
        user = authenticate(username=data["email"], password=data["password"])

        if not user:
            raise serializers.ValidationError("Ungültige Anmeldedaten.")

        if not user.is_verified_email:
            raise serializers.ValidationError(
                "Bitte verifizieren Sie zuerst Ihre E-Mail-Adresse."
            )

        data["user"] = user
        return data


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model."""

    price_euro = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, source="price_euro"
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "sku",
            "name",
            "description",
            "price_cents",
            "price_euro",
            "available",
            "max_per_order",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for OrderItem model."""

    product_name = serializers.CharField(source="product.name", read_only=True)
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    subtotal_cents = serializers.IntegerField(read_only=True)
    subtotal_euro = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "product_name",
            "product_sku",
            "quantity",
            "unit_price_cents",
            "subtotal_cents",
            "subtotal_euro",
        ]
        read_only_fields = ["id", "unit_price_cents"]


class OrderItemCreateSerializer(serializers.Serializer):
    """Serializer for creating order items."""

    sku = serializers.CharField()
    quantity = serializers.IntegerField(min_value=1)

    def validate_sku(self, value):
        """Validate that product exists and is available."""
        try:
            product = Product.objects.get(sku=value)
            if not product.available:
                raise serializers.ValidationError(
                    f"Produkt '{product.name}' ist nicht verfügbar."
                )
            return value
        except Product.DoesNotExist:
            raise serializers.ValidationError(
                f"Produkt mit SKU '{value}' existiert nicht."
            )

    def validate(self, data):
        """Validate quantity against product max_per_order."""
        product = Product.objects.get(sku=data["sku"])
        if data["quantity"] > product.max_per_order:
            raise serializers.ValidationError(
                {
                    "quantity": f"Maximale Menge für '{product.name}' ist {product.max_per_order}."
                }
            )
        return data


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for Order model."""

    items = OrderItemSerializer(many=True, read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)
    total_euro = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "user_email",
            "status",
            "total_cents",
            "total_euro",
            "placed_at",
            "exported_at",
            "created_at",
            "updated_at",
            "items",
        ]
        read_only_fields = [
            "id",
            "user",
            "status",
            "total_cents",
            "placed_at",
            "exported_at",
            "created_at",
            "updated_at",
        ]


class OrderCreateSerializer(serializers.Serializer):
    """Serializer for creating orders."""

    items = OrderItemCreateSerializer(many=True)

    def validate_items(self, value):
        """Validate that items list is not empty."""
        if not value:
            raise serializers.ValidationError(
                "Bestellung muss mindestens ein Produkt enthalten."
            )
        return value

    def create(self, validated_data):
        """Create order with items."""
        items_data = validated_data.pop("items")
        user = self.context["request"].user

        # Create order
        order = Order.objects.create(user=user, status="DRAFT")

        # Create order items
        for item_data in items_data:
            product = Product.objects.get(sku=item_data["sku"])
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item_data["quantity"],
                unit_price_cents=product.price_cents,
            )

        # Calculate total
        order.calculate_total()

        return order


class ExportLogSerializer(serializers.ModelSerializer):
    """Serializer for ExportLog model."""

    class Meta:
        model = ExportLog
        fields = ["id", "run_at", "orders_exported", "status", "details"]
        read_only_fields = ["id", "run_at"]
