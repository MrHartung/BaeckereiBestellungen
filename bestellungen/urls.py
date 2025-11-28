"""
URL configuration for bestellungen app (frontend).
"""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("verify-email/<str:token>/", views.verify_email_view, name="verify_email"),
    path("products/", views.product_list, name="product_list"),
    path("cart/", views.cart_view, name="cart"),
    path("checkout/", views.checkout_view, name="checkout"),
    path("orders/", views.order_list, name="order_list"),
    path("orders/<int:order_id>/", views.order_detail, name="order_detail"),
    path("orders/<int:order_id>/reorder/", views.reorder_view, name="reorder"),
    path("orders/<int:order_id>/cancel/", views.cancel_order_view, name="cancel_order"),
    path(
        "orders/<int:order_id>/request-change/",
        views.request_change_view,
        name="request_change",
    ),
    path("profile/", views.profile_view, name="profile"),
    path("profile/address/", views.update_address_view, name="update_address"),
    path("costs/", views.costs_view, name="costs"),
]
