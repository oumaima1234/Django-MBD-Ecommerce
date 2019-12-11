from django.shortcuts import render, redirect
from .models import Item, OrderItem, Order
from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from django.utils import timezone


# Create your views here.
def checkout(request):
	return render(request, "checkout.html")

class HomeView(ListView):
	model = Item
	context_object_name = "Items"
	template_name = "home.html"
	
class ItemDetailView(ListView):
	model = Item
	context_object_name = "product"
	template_name = "product.html"

def add_to_chart(request, id):
    item = get_object_or_404(Item, id=id)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__id=item.id).exists():
            order_item.quantity += 1
            order_item.save()
            #messages.info(request, "This item quantity was updated.")
            #return redirect("core:order-summary")
        else:
            order.items.add(order_item)
            #messages.info(request, "This item was added to your cart.")
            #return redirect("core:order-summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        #messages.info(request, "This item was added to your cart.")
        #return redirect("core:order-summary")
    return redirect("core:product", id=id)

def remove_from_cart(request, id):
    item = get_object_or_404(Item, id=id)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__id=item.id).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            #messages.info(request, "This item was removed from your cart.")
            return redirect("core:order-summary")
        else:
            #messages.info(request, "This item was not in your cart")
            return redirect("core:product", id=id)
    else:
        # messages.info(request, "You do not have an active order")
        return redirect("core:product", id=id)
