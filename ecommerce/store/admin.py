from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import *

# Register your models here.


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "image_tag",
        "category",
        "price",
        "created_at",
        "updated_at",
        "edit_link",
        "delete_link",
    )
    list_filter = ("category", "created_at", "updated_at")
    search_fields = ("name", "description")

    def image_tag(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" />'.format(obj.image.url)
            )
        else:
            return ""

    image_tag.short_description = "Image"

    def edit_link(self, obj):
        if obj.id:
            url = reverse("admin:store_product_change", args=[obj.id])
            return format_html('<a href="{}">Edit</a>'.format(url))
        else:
            return ""

    edit_link.short_description = "Edit"

    def delete_link(self, obj):
        if obj.id:
            url = reverse("admin:store_product_delete", args=[obj.id])
            return format_html('<a href="{}">Delete</a>'.format(url))
        else:
            return ""

    delete_link.short_description = "Delete"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "transaction_id",
        "customer",
        "date_ordered",
        "get_cart_items",
        "get_cart_total",
        "complete",
    )
    list_filter = ("customer", "date_ordered", "complete")
    search_fields = ("id", "user__username", "user__email")

    inlines = [OrderItemInline]


admin.site.register(Customer)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(Product, ProductAdmin)
admin.site.register(ShippingAddres)
admin.site.register(Categorie)
