"""
API views for the bestellungen app.
"""

from django.contrib.auth import login, logout
from django.core.management import call_command
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import CustomUser, ExportLog, Order, Product
from .serializers import (
    ExportLogSerializer,
    LoginSerializer,
    OrderCreateSerializer,
    OrderSerializer,
    ProductSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)


class IsAdminUser(permissions.BasePermission):
    """Permission class for admin-only endpoints."""

    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class AuthViewSet(viewsets.GenericViewSet):
    """ViewSet for authentication operations."""

    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=["post"])
    def register(self, request):
        """Register a new user."""
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "message": "Registrierung erfolgreich. Bitte überprüfen Sie Ihre E-Mails zur Verifizierung.",
                    "user": UserSerializer(user).data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def login(self, request):
        """Login user and return token."""
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            login(request, user)

            # Create or get token
            token, created = Token.objects.get_or_create(user=user)

            return Response({"token": token.key, "user": UserSerializer(user).data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )
    def logout(self, request):
        """Logout user and delete token."""
        if hasattr(request.user, "auth_token"):
            request.user.auth_token.delete()
        logout(request)
        return Response({"message": "Erfolgreich abgemeldet."})

    @action(detail=False, methods=["post"])
    def verify_email(self, request):
        """Verify user email with token."""
        token = request.data.get("token")
        if not token:
            return Response(
                {"error": "Token erforderlich."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = CustomUser.objects.get(email_verification_token=token)
            if user.verify_email(token):
                return Response({"message": "E-Mail erfolgreich verifiziert."})
            else:
                return Response(
                    {"error": "Ungültiger Token."}, status=status.HTTP_400_BAD_REQUEST
                )
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "Ungültiger Token."}, status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=["post"])
    def password_reset(self, request):
        """Request password reset (placeholder for now)."""
        email = request.data.get("email")
        if not email:
            return Response(
                {"error": "E-Mail erforderlich."}, status=status.HTTP_400_BAD_REQUEST
            )

        # TODO: Implement password reset logic
        return Response(
            {
                "message": "Falls ein Konto mit dieser E-Mail existiert, wurde eine Passwort-Reset-E-Mail gesendet."
            }
        )


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Product operations."""

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "sku"

    def get_queryset(self):
        """Filter available products by default."""
        queryset = super().get_queryset()
        available = self.request.query_params.get("available", "true")

        if available.lower() == "true":
            queryset = queryset.filter(available=True)

        return queryset

    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    def list(self, request, *args, **kwargs):
        """List products with caching."""
        return super().list(request, *args, **kwargs)


class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet for Order operations."""

    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return orders for the current user only."""
        return Order.objects.filter(user=self.request.user).prefetch_related(
            "items__product"
        )

    def get_serializer_class(self):
        """Use different serializer for creation."""
        if self.action == "create":
            return OrderCreateSerializer
        return OrderSerializer

    def create(self, request, *args, **kwargs):
        """Create a new order."""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            order = serializer.save()
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def place(self, request, pk=None):
        """Place an order (change status from DRAFT to PLACED)."""
        order = self.get_object()

        try:
            order.place_order()
            return Response(OrderSerializer(order).data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """Cancel an order."""
        order = self.get_object()

        try:
            order.cancel_order()
            return Response(OrderSerializer(order).data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ExportViewSet(viewsets.GenericViewSet):
    """ViewSet for export operations (admin only)."""

    permission_classes = [IsAdminUser]
    serializer_class = ExportLogSerializer

    @action(detail=False, methods=["post"])
    def run(self, request):
        """Trigger export to Access database."""
        try:
            # Call the management command
            call_command("export_orders")

            # Get the latest export log
            latest_log = ExportLog.objects.first()

            return Response(
                ExportLogSerializer(latest_log).data, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=["get"])
    def logs(self, request):
        """List export logs."""
        logs = ExportLog.objects.all()[:50]  # Last 50 logs
        serializer = ExportLogSerializer(logs, many=True)
        return Response(serializer.data)
