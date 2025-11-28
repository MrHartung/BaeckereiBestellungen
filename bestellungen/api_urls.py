"""
API URL configuration for bestellungen app.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api_views import AuthViewSet, ExportViewSet, OrderViewSet, ProductViewSet

router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="product")
router.register(r"orders", OrderViewSet, basename="order")
router.register(r"admin/export", ExportViewSet, basename="export")

# Auth endpoints are registered manually since they don't follow standard REST patterns
auth_patterns = [
    path(
        "auth/register/",
        AuthViewSet.as_view({"post": "register"}),
        name="auth-register",
    ),
    path("auth/login/", AuthViewSet.as_view({"post": "login"}), name="auth-login"),
    path("auth/logout/", AuthViewSet.as_view({"post": "logout"}), name="auth-logout"),
    path(
        "auth/verify-email/",
        AuthViewSet.as_view({"post": "verify_email"}),
        name="auth-verify-email",
    ),
    path(
        "auth/password-reset/",
        AuthViewSet.as_view({"post": "password_reset"}),
        name="auth-password-reset",
    ),
]

urlpatterns = auth_patterns + [
    path("", include(router.urls)),
]
