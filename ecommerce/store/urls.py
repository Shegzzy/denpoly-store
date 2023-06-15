from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("cart/", views.cart, name="cart"),
    path("about_us/", views.aboutUs, name="about_us"),
    path("contact_us/", views.contact_page, name="contact_us"),
    path("get-products/", views.get_products, name="get_products"),
    path("checkout/", views.checkout, name="checkout"),
    path("update_item/", views.updateItem, name="update_item"),
    path("cart_data/", views.cart_data, name="cart_data"),
    path("process_order/", views.processOrder, name="process_order"),
    path("paystack_verify/", views.verifyPayment, name="paystack_verify"),
    path(
        "product_details/<slug:slug>/",
        views.productDetails,
        name="product_details",
    ),
]
