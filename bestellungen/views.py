"""
Views for the bestellungen app frontend.
"""

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .forms import LoginForm, RegistrationForm
from .models import CustomUser, Order, OrderItem, Product


def home(request):
    """Home page view."""
    return render(request, "bestellungen/home.html")


def register_view(request):
    """User registration view."""
    if request.user.is_authenticated:
        return redirect("product_list")

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            token = user.generate_verification_token()

            # Send verification email (already handled in form)
            messages.success(
                request,
                "Registrierung erfolgreich! Bitte überprüfen Sie Ihre E-Mails zur Verifizierung.",
            )
            return redirect("login")
    else:
        form = RegistrationForm()

    return render(request, "bestellungen/register.html", {"form": form})


def login_view(request):
    """User login view."""
    if request.user.is_authenticated:
        return redirect("product_list")

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            user = authenticate(request, username=email, password=password)

            if user is not None:
                if not user.is_verified_email:
                    messages.error(
                        request, "Bitte verifizieren Sie zuerst Ihre E-Mail-Adresse."
                    )
                else:
                    login(request, user)
                    messages.success(request, f"Willkommen zurück, {user.first_name}!")
                    return redirect("product_list")
            else:
                messages.error(request, "Ungültige Anmeldedaten.")
    else:
        form = LoginForm()

    return render(request, "bestellungen/login.html", {"form": form})


def logout_view(request):
    """User logout view."""
    logout(request)
    messages.success(request, "Sie wurden erfolgreich abgemeldet.")
    return redirect("home")


def verify_email_view(request, token):
    """Email verification view."""
    try:
        user = CustomUser.objects.get(email_verification_token=token)
        if user.verify_email(token):
            messages.success(
                request,
                "E-Mail erfolgreich verifiziert! Sie können sich jetzt anmelden.",
            )
            return redirect("login")
        else:
            messages.error(request, "Ungültiger Verifizierungs-Token.")
    except CustomUser.DoesNotExist:
        messages.error(request, "Ungültiger Verifizierungs-Token.")

    return redirect("home")


def product_list(request):
    """Product list view."""
    products = Product.objects.filter(available=True).order_by("name")
    return render(request, "bestellungen/product_list.html", {"products": products})


@login_required
def cart_view(request):
    """Shopping cart view."""
    # Get or create draft order for user
    order, created = Order.objects.get_or_create(user=request.user, status="DRAFT")

    if request.method == "POST":
        product_id = request.POST.get("product_id")
        quantity = int(request.POST.get("quantity", 1))
        action = request.POST.get("action")

        if action == "add":
            product = get_object_or_404(Product, id=product_id, available=True)

            if quantity > product.max_per_order:
                messages.error(
                    request,
                    f"Maximale Menge für {product.name} ist {product.max_per_order}.",
                )
            else:
                # Add or update item in cart
                order_item, created = OrderItem.objects.get_or_create(
                    order=order,
                    product=product,
                    defaults={
                        "quantity": quantity,
                        "unit_price_cents": product.price_cents,
                    },
                )

                if not created:
                    order_item.quantity += quantity
                    if order_item.quantity > product.max_per_order:
                        order_item.quantity = product.max_per_order
                    order_item.save()

                order.calculate_total()
                messages.success(
                    request, f"{product.name} wurde zum Warenkorb hinzugefügt."
                )

        elif action == "remove":
            OrderItem.objects.filter(order=order, product_id=product_id).delete()
            order.calculate_total()
            messages.success(request, "Artikel wurde aus dem Warenkorb entfernt.")

        elif action == "update":
            order_item = get_object_or_404(
                OrderItem, order=order, product_id=product_id
            )
            if quantity <= 0:
                order_item.delete()
            else:
                if quantity > order_item.product.max_per_order:
                    quantity = order_item.product.max_per_order
                order_item.quantity = quantity
                order_item.save()
            order.calculate_total()

        return redirect("cart")

    return render(request, "bestellungen/cart.html", {"order": order})


@login_required
def checkout_view(request):
    """Checkout view."""
    try:
        order = Order.objects.get(user=request.user, status="DRAFT")
    except Order.DoesNotExist:
        messages.error(request, "Kein Warenkorb gefunden.")
        return redirect("product_list")

    if not order.items.exists():
        messages.error(request, "Ihr Warenkorb ist leer.")
        return redirect("product_list")

    if request.method == "POST":
        # Save delivery information
        order.delivery_type = request.POST.get("delivery_type", "DELIVERY")

        # Parse desired time if provided
        desired_date = request.POST.get("desired_date")
        desired_time_str = request.POST.get("desired_time")
        if desired_date and desired_time_str:
            from datetime import datetime

            datetime_str = f"{desired_date} {desired_time_str}"
            order.desired_time = timezone.datetime.strptime(
                datetime_str, "%Y-%m-%d %H:%M"
            )

        # Save delivery address
        if order.delivery_type == "DELIVERY":
            order.delivery_street = request.POST.get(
                "delivery_street", request.user.default_street
            )
            order.delivery_city = request.POST.get(
                "delivery_city", request.user.default_city
            )
            order.delivery_postal_code = request.POST.get(
                "delivery_postal_code", request.user.default_postal_code
            )
            order.delivery_phone = request.POST.get(
                "delivery_phone", request.user.default_phone
            )
            order.delivery_notes = request.POST.get("delivery_notes", "")

        order.save()

        try:
            order.place_order()
            # Create new empty cart for user
            Order.objects.create(user=request.user, status="DRAFT")
            messages.success(
                request, f"Bestellung #{order.id} wurde erfolgreich aufgegeben!"
            )
            return redirect("order_detail", order_id=order.id)
        except ValueError as e:
            messages.error(request, str(e))

    # Pre-fill with user's default address
    if not order.delivery_street and request.user.default_street:
        order.delivery_street = request.user.default_street
        order.delivery_city = request.user.default_city
        order.delivery_postal_code = request.user.default_postal_code
        order.delivery_phone = request.user.default_phone

    return render(request, "bestellungen/checkout.html", {"order": order})


@login_required
def order_list(request):
    """Order history view."""
    orders = (
        Order.objects.filter(user=request.user)
        .exclude(status="DRAFT")
        .order_by("-placed_at")
    )

    return render(request, "bestellungen/order_list.html", {"orders": orders})


@login_required
def order_detail(request, order_id):
    """Order detail view."""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "bestellungen/order_detail.html", {"order": order})


@login_required
def profile_view(request):
    """User profile view."""
    order_count = (
        Order.objects.filter(user=request.user).exclude(status="DRAFT").count()
    )
    return render(
        request,
        "bestellungen/profile.html",
        {"user": request.user, "order_count": order_count},
    )


@login_required
def update_address_view(request):
    """Update user's default delivery address."""
    if request.method == "POST":
        request.user.default_street = request.POST.get("street", "")
        request.user.default_city = request.POST.get("city", "")
        request.user.default_postal_code = request.POST.get("postal_code", "")
        request.user.default_phone = request.POST.get("phone", "")
        request.user.save()
        messages.success(request, "Lieferadresse wurde aktualisiert.")
        return redirect("profile")

    return render(request, "bestellungen/update_address.html", {"user": request.user})


@login_required
def reorder_view(request, order_id):
    """Repeat a previous order by adding items to cart."""
    original_order = get_object_or_404(Order, id=order_id, user=request.user)

    if original_order.status == "DRAFT":
        messages.error(request, "Diese Bestellung kann nicht wiederholt werden.")
        return redirect("order_list")

    # Get or create draft order (cart)
    cart, created = Order.objects.get_or_create(user=request.user, status="DRAFT")

    # Copy items from original order to cart
    items_added = 0
    for item in original_order.items.all():
        if item.product.available:
            # Check if item already in cart
            cart_item, created = OrderItem.objects.get_or_create(
                order=cart,
                product=item.product,
                defaults={
                    "quantity": item.quantity,
                    "unit_price_cents": item.product.price_cents,
                },
            )

            if not created:
                # Update quantity if item already exists
                cart_item.quantity += item.quantity
                if cart_item.quantity > item.product.max_per_order:
                    cart_item.quantity = item.product.max_per_order
                cart_item.save()

            items_added += 1

    cart.calculate_total()

    if items_added > 0:
        messages.success(
            request,
            f"{items_added} Artikel aus Bestellung #{order_id} wurden zum Warenkorb hinzugefügt.",
        )
    else:
        messages.warning(
            request, "Keine Artikel konnten hinzugefügt werden (nicht verfügbar)."
        )

    return redirect("cart")


@login_required
def cancel_order_view(request, order_id):
    """Cancel an order (only before 22:00 cutoff)."""
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if not order.is_cancellable:
        messages.error(
            request,
            "Diese Bestellung kann nicht mehr storniert werden. "
            "Bitte verwenden Sie die Änderungsanfrage.",
        )
        return redirect("order_detail", order_id=order.id)

    if request.method == "POST":
        order.status = "CANCELLED"
        order.save(update_fields=["status"])
        messages.success(request, f"Bestellung #{order.id} wurde storniert.")
        return redirect("order_list")

    return render(request, "bestellungen/cancel_order.html", {"order": order})


@login_required
def request_change_view(request, order_id):
    """Request a change or cancellation for an exported order."""
    from .models import OrderChangeRequest

    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status not in ["PLACED", "EXPORTED"]:
        messages.error(
            request, "Für diese Bestellung kann keine Änderung angefragt werden."
        )
        return redirect("order_detail", order_id=order.id)

    # Check if there's already a pending request
    existing_request = OrderChangeRequest.objects.filter(
        order=order, status="PENDING"
    ).first()

    if existing_request:
        messages.warning(
            request,
            "Es gibt bereits eine ausstehende Änderungsanfrage für diese Bestellung.",
        )
        return redirect("order_detail", order_id=order.id)

    if request.method == "POST":
        request_type = request.POST.get("request_type")
        reason = request.POST.get("reason", "")

        if request_type and reason:
            OrderChangeRequest.objects.create(
                order=order, request_type=request_type, reason=reason
            )
            messages.success(
                request,
                "Ihre Änderungsanfrage wurde übermittelt. "
                "Sie werden per E-Mail über die Entscheidung informiert.",
            )
            return redirect("order_detail", order_id=order.id)
        else:
            messages.error(request, "Bitte füllen Sie alle Felder aus.")

    return render(request, "bestellungen/request_change.html", {"order": order})


@login_required
def costs_view(request):
    """Show cost overview for week and month."""
    from datetime import timedelta

    from django.db.models import Sum

    now = timezone.now()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    # Calculate costs
    week_orders = Order.objects.filter(
        user=request.user, status__in=["PLACED", "EXPORTED"], placed_at__gte=week_ago
    )

    month_orders = Order.objects.filter(
        user=request.user, status__in=["PLACED", "EXPORTED"], placed_at__gte=month_ago
    )

    week_total = sum(order.grand_total_cents for order in week_orders) / 100
    month_total = sum(order.grand_total_cents for order in month_orders) / 100

    context = {
        "week_total": week_total,
        "month_total": month_total,
        "week_orders": week_orders,
        "month_orders": month_orders,
    }

    return render(request, "bestellungen/costs.html", context)
