from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
import json
import datetime
from .models import *
from .util import cookieCart, cartData, guestOder
from django.http import JsonResponse
import secrets


# from django.views.decorators.csrf import csrf_exempt


# @csrf_exempt
# Create your views here.
def index(request):
    data = cartData(request)
    customer = None
    if request.user.is_authenticated:
        try:
            customer = Customer.objects.get(user=request.user)
        except Customer.DoesNotExist:
            pass
    cartItems = data["cartItems"]
    order = data["order"]
    items = data["items"]
    categories = Categorie.objects.all()

    # Check if category is selected
    category_slug = request.GET.get("category")
    if category_slug:
        category = get_object_or_404(Categorie, slug=category_slug)
        products = Product.objects.filter(category=category)
        paginator_products = Paginator(products, 9)
        page_number_products = request.GET.get("product_page")
        page_obj_products = paginator_products.get_page(page_number_products)
        selected_category = category
    else:
        products = Product.objects.all()
        paginator_products = Paginator(products, 9)
        page_number_products = request.GET.get("product_page")
        page_obj_products = paginator_products.get_page(page_number_products)
        selected_category = None

    context = {
        "cartItems": cartItems,
        "order": order,
        "items": items,
        "categories": categories,
        "products": products,
        "page_obj_products": page_obj_products,
        "selected_category": selected_category,
        "customer": customer,  # include customer in the context
    }
    return render(request, "store/index.html", context)


def register(request):
    if request.method == "POST":
        # Get form data
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        phone_number = request.POST.get("phone_number")
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        # Create customer
        customer = Customer.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
        )
        customer.save()

        # Authenticate user and log them in
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You have successfully registered and logged in!")
            return redirect("index")

    return render(request, "registration/login-register.html")


def user_login(request):
    page = "login"
    context = {"page": page}

    if request.user.is_authenticated:
        return redirect("index")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            messages.error(request, "User does not exist")
            return render(request, "registration/login-register.html", context)

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(reverse("index"))
        else:
            messages.error(request, "Invalid email or password")
            return render(request, "registration/login-register.html", context)

    else:
        return render(request, "registration/login-register.html", context)


def user_logout(request):
    logout(request)
    return redirect("index")


def cart(request):
    data = cartData(request)
    cartItems = data["cartItems"]
    order = data["order"]
    items = data["items"]

    context = {"items": items, "order": order, "cartItems": cartItems}
    return render(request, "store/cart.html", context)


def productDetails(request, product_id):
    data = cartData(request)
    product = get_object_or_404(Product, id=product_id)
    cartItems = data["cartItems"]
    order = data["order"]
    items = data["items"]

    context = {
        "items": items,
        "order": order,
        "cartItems": cartItems,
        "product": product,
    }
    return render(request, "store/single-product.html", context)


def checkout(request):
    data = cartData(request)
    cartItems = data["cartItems"]
    order = data["order"]
    items = data["items"]
    context = {"items": items, "order": order, "cartItems": cartItems}
    return render(request, "store/checkout.html", context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data["productId"]
    action = data["action"]

    # print("action:", action)
    # print("productId:", productId)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        cookieData = cookieCart(request)
        order, created = guestOder(request, cookieData)

    product = Product.objects.get(id=productId)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == "add":
        orderItem.quantity = orderItem.quantity + 1
    elif action == "remove":
        orderItem.quantity = orderItem.quantity - 1

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse("Item was added", safe=False)


def processOrder(request):
    transaction_id = secrets.token_urlsafe(20)
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

    else:
        customer, order = guestOder(request, data)

    total = float(data["form"]["total"])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddres.objects.create(
            customer=customer,
            order=order,
            address=data["shipping"]["address"],
            state=data["shipping"]["state"],
            city=data["shipping"]["city"],
            phone=data["shipping"]["phone"],
        )
    return JsonResponse("Payment Completed!", safe=False)
