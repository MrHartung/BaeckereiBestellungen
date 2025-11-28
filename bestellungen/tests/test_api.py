"""
Tests for API views.
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from bestellungen.models import CustomUser, Order, OrderItem, Product


@pytest.fixture
def api_client():
    """Create API client."""
    return APIClient()


@pytest.fixture
def user():
    """Create a verified user."""
    return CustomUser.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass1234567890",
        first_name="Test",
        last_name="User",
        is_verified_email=True,
    )


@pytest.fixture
def unverified_user():
    """Create an unverified user."""
    return CustomUser.objects.create_user(
        username="unverified",
        email="unverified@example.com",
        password="testpass1234567890",
        is_verified_email=False,
    )


@pytest.fixture
def product():
    """Create a test product."""
    return Product.objects.create(
        sku="TEST-001",
        name="Test Product",
        price_cents=250,
        available=True,
        max_per_order=10,
    )


@pytest.mark.django_db
class TestAuthAPI:
    """Tests for authentication API."""

    def test_register_user(self, api_client):
        """Test user registration."""
        url = reverse("auth-register")
        data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "first_name": "New",
            "last_name": "User",
            "password": "testpass1234567890",
            "password_confirm": "testpass1234567890",
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert "user" in response.data
        assert CustomUser.objects.filter(email="newuser@example.com").exists()

    def test_register_with_mismatched_passwords_fails(self, api_client):
        """Test registration with mismatched passwords."""
        url = reverse("auth-register")
        data = {
            "email": "test@example.com",
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "password": "testpass1234567890",
            "password_confirm": "differentpass1234567890",
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_success(self, api_client, user):
        """Test successful login."""
        url = reverse("auth-login")
        data = {"email": "test@example.com", "password": "testpass1234567890"}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert "token" in response.data
        assert "user" in response.data

    def test_login_unverified_user_fails(self, api_client, unverified_user):
        """Test that unverified users cannot login."""
        url = reverse("auth-login")
        data = {"email": "unverified@example.com", "password": "testpass1234567890"}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestProductAPI:
    """Tests for product API."""

    def test_list_products(self, api_client, product):
        """Test listing products."""
        url = reverse("product-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) >= 1

    def test_get_product_by_sku(self, api_client, product):
        """Test getting product by SKU."""
        url = reverse("product-detail", kwargs={"sku": "TEST-001"})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["sku"] == "TEST-001"
        assert response.data["name"] == "Test Product"


@pytest.mark.django_db
class TestOrderAPI:
    """Tests for order API."""

    def test_create_order_requires_auth(self, api_client):
        """Test that creating order requires authentication."""
        url = reverse("order-list")
        data = {"items": [{"sku": "TEST-001", "quantity": 2}]}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_order_success(self, api_client, user, product):
        """Test successful order creation."""
        api_client.force_authenticate(user=user)

        url = reverse("order-list")
        data = {"items": [{"sku": "TEST-001", "quantity": 2}]}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["status"] == "DRAFT"
        assert len(response.data["items"]) == 1

    def test_place_order(self, api_client, user, product):
        """Test placing an order."""
        api_client.force_authenticate(user=user)

        # Create order
        order = Order.objects.create(user=user)
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=2,
            unit_price_cents=product.price_cents,
        )

        # Place order
        url = reverse("order-place", kwargs={"pk": order.id})
        response = api_client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "PLACED"
        assert response.data["placed_at"] is not None

    def test_list_user_orders(self, api_client, user, product):
        """Test listing user's orders."""
        api_client.force_authenticate(user=user)

        # Create order
        order = Order.objects.create(user=user)
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=1,
            unit_price_cents=product.price_cents,
        )
        order.place_order()

        url = reverse("order-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) >= 1
