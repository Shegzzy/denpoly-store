from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
import json
import requests
from django.conf import settings
from .models import *
from .util import cookieCart, cartData, guestOder
from django.http import JsonResponse
import secrets


# from django.views.decorators.csrf import csrf_exempt


# @csrf_exempt
# Create your views here.
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render
from .models import Categorie, Product


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
        "page_obj_products": page_obj_products,
        "selected_category": selected_category,
        "customer": customer,
        "products": page_obj_products,
    }
    return render(request, "store/index.html", context)


def get_products(request):
    category_slug = request.GET.get("category")
    category = get_object_or_404(Categorie, slug=category_slug)
    products = Product.objects.filter(category=category)
    paginator_products = Paginator(products, 9)
    page_number_products = request.GET.get("product_page")
    page_obj_products = paginator_products.get_page(page_number_products)
    context = {
        "products": page_obj_products,
        "page_obj_products": page_obj_products,
    }
    return render(request, "category_products/products.html", context)


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


def aboutUs(request):
    data = cartData(request)
    cartItems = data["cartItems"]
    order = data["order"]
    items = data["items"]

    context = {"items": items, "order": order, "cartItems": cartItems}
    return render(request, "store/about_us.html", context)


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
    paystack_public_key = settings.PAYSTACK_PUBLIC_KEY
    context = {
        "items": items,
        "order": order,
        "cartItems": cartItems,
        "paystack_public_key": paystack_public_key,
    }
    return render(request, "store/checkout.html", context)


def cart_data(request):
    data = cartData(request)
    cartItems = data["cartItems"]
    order = data["order"]
    items = data["items"]
    mini_cart_html = render(
        request, "mini_cart/mini_cart.html", {"items": items, "order": order}
    ).content.decode("utf-8")
    # Serialize the cart data into JSON format
    response_data = {
        "miniCartHTML": mini_cart_html,
        "cartItems": cartItems,
        "order": {
            "get_cart_total": order["get_cart_total"],
            "get_cart_items": order["get_cart_items"],
            "shipping": order["shipping"],
        },
        "items": {
            item["product"]["id"]: {
                "quantity": item["quantity"],
                "get_total": item["get_total"],
            }
            for item in items
        },
    }

    return JsonResponse(response_data)


def updateItem(request):
    data = json.loads(request.body)
    datas = cartData(request)
    productId = data["productId"]
    action = data["action"]
    items = datas["items"]

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
        messages.success(request, "Item added to cart")
    elif action == "remove":
        orderItem.quantity = orderItem.quantity - 1
        messages.success(request, "Item removed from cart")
    elif action == "delete":
        orderItem.quantity = 0
        messages.success(request, "Item deleted from cart")

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    # Update the items variable with the updated order items
    items = OrderItem.objects.filter(order=order)

    cart_items_count = order.get_cart_items
    cart_items_total = order.get_cart_total
    items_quantity = orderItem.quantity
    singleProduct_total = orderItem.get_total
    mini_cart_html = render(
        request, "mini_cart/mini_cart.html", {"items": items, "order": order}
    ).content.decode("utf-8")
    message_text = [str(message) for message in messages.get_messages(request)]

    response_data = {
        "message": message_text,
        "cartItems": cart_items_count,
        "cartTotal": cart_items_total,
        "itemsQuantity": items_quantity,
        "productTotal": singleProduct_total,
        "miniCartHTML": mini_cart_html,
    }

    return JsonResponse(response_data)


def verifyPayment(reference):
    print("verifying payment")
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # Payment verification successful
        payment_data = response.json()["data"]
        # Extract necessary payment details
        status = payment_data["status"]
        amount = payment_data["amount"] / 100  # Convert amount to the correct currency
        # You can perform additional actions here based on the payment status and amount
        return status, amount
    else:
        # Payment verification failed
        return None, None


def processOrder(request):
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        customer, order = guestOder(request, data)

    total = float(data["form"]["total"])
    transaction_id = data["reference"]

    if total == order.get_cart_total:
        # Initialize payment request with Paystack
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "email": customer.email,
            "amount": total,
            "callback_url": request.build_absolute_uri(reverse("paystack_verify")),
        }
        print(payload)
        response = requests.post(
            "https://api.paystack.co/transaction/initialize",
            headers=headers,
            json=payload,
        )
        print(response)

        if response.status_code == 200:
            # Redirect customer to Paystack payment page
            payment_url = response.json()["data"]["authorization_url"]
            status, amount = verifyPayment(transaction_id)
            if status == "success":
                # Payment verification successful
                order.transaction_id = transaction_id
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
            else:
                # Payment verification failed or status is not success
                # Handle the error accordingly
                print("Verification failed")
            return JsonResponse(payment_url, safe=False)
        else:
            # Payment request failed
            return JsonResponse(response.json(), safe=False, status=400)
    order.save()

    return JsonResponse("Payment Completed!", safe=False)
