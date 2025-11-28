"""
Tests for models.
"""
import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from bestellungen.models import CustomUser, Product, Order, OrderItem


@pytest.mark.django_db
class TestCustomUser:
    """Tests for CustomUser model."""
    
    def test_create_user(self):
        """Test user creation."""
        user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        assert user.email == 'test@example.com'
        assert user.is_verified_email is False
        assert user.check_password('testpass123')
    
    def test_generate_verification_token(self):
        """Test email verification token generation."""
        user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        token = user.generate_verification_token()
        
        assert token is not None
        assert len(token) > 20
        assert user.email_verification_token == token
        assert user.email_verification_sent_at is not None
    
    def test_verify_email(self):
        """Test email verification."""
        user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        token = user.generate_verification_token()
        result = user.verify_email(token)
        
        assert result is True
        assert user.is_verified_email is True
        assert user.email_verification_token is None


@pytest.mark.django_db
class TestProduct:
    """Tests for Product model."""
    
    def test_create_product(self):
        """Test product creation."""
        product = Product.objects.create(
            sku='TEST-001',
            name='Test Product',
            description='A test product',
            price_cents=250,
            available=True,
            max_per_order=10
        )
        
        assert product.sku == 'TEST-001'
        assert product.price_euro == 2.5
        assert str(product) == 'Test Product (TEST-001)'
    
    def test_price_euro_property(self):
        """Test price_euro calculated property."""
        product = Product.objects.create(
            sku='TEST-002',
            name='Test Product 2',
            price_cents=1550
        )
        
        assert product.price_euro == 15.5


@pytest.mark.django_db
class TestOrder:
    """Tests for Order model."""
    
    @pytest.fixture
    def user(self):
        """Create a test user."""
        return CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            is_verified_email=True
        )
    
    @pytest.fixture
    def product(self):
        """Create a test product."""
        return Product.objects.create(
            sku='TEST-001',
            name='Test Product',
            price_cents=250,
            available=True
        )
    
    def test_create_order(self, user):
        """Test order creation."""
        order = Order.objects.create(user=user)
        
        assert order.status == 'DRAFT'
        assert order.total_cents == 0
        assert order.placed_at is None
    
    def test_calculate_total(self, user, product):
        """Test order total calculation."""
        order = Order.objects.create(user=user)
        
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=3,
            unit_price_cents=product.price_cents
        )
        
        total = order.calculate_total()
        
        assert total == 750  # 3 * 250
        assert order.total_cents == 750
    
    def test_place_order(self, user, product):
        """Test placing an order."""
        order = Order.objects.create(user=user)
        
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=2,
            unit_price_cents=product.price_cents
        )
        
        order.place_order()
        
        assert order.status == 'PLACED'
        assert order.placed_at is not None
        assert order.total_cents == 500
    
    def test_place_order_without_items_fails(self, user):
        """Test that placing order without items raises error."""
        order = Order.objects.create(user=user)
        
        with pytest.raises(ValueError, match="Order has no items"):
            order.place_order()
    
    def test_cancel_order(self, user, product):
        """Test canceling an order."""
        order = Order.objects.create(user=user)
        
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=1,
            unit_price_cents=product.price_cents
        )
        
        order.place_order()
        order.cancel_order()
        
        assert order.status == 'CANCELLED'
    
    def test_cannot_cancel_exported_order(self, user, product):
        """Test that exported orders cannot be cancelled."""
        order = Order.objects.create(user=user)
        
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=1,
            unit_price_cents=product.price_cents
        )
        
        order.place_order()
        order.status = 'EXPORTED'
        order.exported_at = timezone.now()
        order.save()
        
        with pytest.raises(ValueError, match="Exported orders cannot be cancelled"):
            order.cancel_order()


@pytest.mark.django_db
class TestOrderItem:
    """Tests for OrderItem model."""
    
    @pytest.fixture
    def user(self):
        """Create a test user."""
        return CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    @pytest.fixture
    def product(self):
        """Create a test product."""
        return Product.objects.create(
            sku='TEST-001',
            name='Test Product',
            price_cents=300,
            available=True,
            max_per_order=5
        )
    
    def test_create_order_item(self, user, product):
        """Test order item creation."""
        order = Order.objects.create(user=user)
        
        item = OrderItem.objects.create(
            order=order,
            product=product,
            quantity=2,
            unit_price_cents=product.price_cents
        )
        
        assert item.quantity == 2
        assert item.unit_price_cents == 300
        assert item.subtotal_cents == 600
        assert item.subtotal_euro == 6.0
    
    def test_order_item_validates_max_per_order(self, user, product):
        """Test that order item respects max_per_order."""
        order = Order.objects.create(user=user)
        
        with pytest.raises(ValidationError):
            item = OrderItem(
                order=order,
                product=product,
                quantity=10,  # More than max_per_order (5)
                unit_price_cents=product.price_cents
            )
            item.save()
    
    def test_order_item_snapshots_price(self, user, product):
        """Test that order item snapshots product price."""
        order = Order.objects.create(user=user)
        
        item = OrderItem.objects.create(
            order=order,
            product=product,
            quantity=1
        )
        
        # Price should be snapshotted from product
        assert item.unit_price_cents == 300
        
        # Change product price
        product.price_cents = 400
        product.save()
        
        # Order item should still have old price
        item.refresh_from_db()
        assert item.unit_price_cents == 300
