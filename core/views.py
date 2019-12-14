from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from .models import Item, OrderItem, Order, BillingAddress, Payment
from django.views.generic import ListView, DetailView, View
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from .forms import checkoutForm
from django.conf import settings

import stripe
stripe.api_key = "sk_test_oZGSabZkMrUeXvX1H6nsBtw000RN4Ixg6e"#settings.STRIPE_SECRET_KEY


# Create your views here.
class checkoutView(View):   
    def get(self, *args, **kwargs):
        form = checkoutForm()
        context = {
             'form': form
        }
        return render(self.request, "checkout.html", context)

    def post(self, *args, **kwargs):
        form = checkoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            print(self.request.POST)
            if form.is_valid():
                print(form.cleaned_data)
                street_address = form.cleaned_data.get('street_address')
                appartement_address = form.cleaned_data.get('appartement_address')
                country = form.cleaned_data.get('country')
                zip = form.cleaned_data.get('zip')
                #same_shipping_address = form.cleaned_data.get('same_shipping_address')
                #save_info = form.cleaned_data.get('save_info')
                payment_option = form.cleaned_data.get('payment_option')
                billing_address = BillingAddress(
                    user=self.request.user,
                    street_address=street_address,
                    appartement_address=appartement_address,
                    country=country,
                    zip=zip
                )
                billing_address.save()
                # do not forget to add the billing to the order
                order.billing_address = billing_address
                order.save()
                print("form is valid")
                if payment_option == 'S':
                    return redirect("core:payment", payment_option='stripe')
                elif payment_option == 'P':
                    return redirect("core:payment", payment_option='paypal')
                else:
                    messages.warning(self.request, "Invalid payment option selected")
                    return redirect("core:checkout")
        except ObjectDoesNotExist:
            messages.error(self.request, "you do not have an active order")
            return redirect('core:order-summary')
  



    '''form_class = checkoutForm
    template_name = 'checkout.html'
    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})
    def post(self,request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            ...
        return render(request, "checkout.html")'''


class PaymentView(View):
    def get(self, *args, **kwargs):
        print("\n\n\n\n\n tetttttttssssssssssss")
        order = Order.objects.get(user=self.request.user, ordered=False) 
        context = {
                'order': order
            }
        return render(self.request, "payment.html", context)

    def post(self, *args, **kwargs):
        print("\n\n\n\n\n tettttttts")
        order = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST.get('stripeToken')
        print("self.request.POST \n", self.request.POST)
        print("token \n", token)
        amount = int(order.get_total() * 100)
        print("amount \n", amount)
        print("\n\n\n\n\n tettttttts1")

        try:
            # Use Stripe's library to make requests...
            print("\n\n\n\n\n tettttttts1.2")
            charge = stripe.Charge.create(
                amount=amount,  # cents
                currency="usd",
                source=token,
            )
            print("\n\n\n\n\n tettttttts2")

            # create payment
            payment = Payment()
            print("\n\n\n\n\n tettttttts3")
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            print("\n\n user", payment.user)
            payment.amount = amount
            print("\n\n payment", payment)
            payment.save()
            print("\n\n\n\n\n tettttttts4")
            # assign payment to the order
            order_items = order.items.all()
            print(order_items)
            order_items.update(ordered=True)
            for item in order_items:
                item.save()
            order.ordered = True
            order.payment = payment
            order.save()
            print("\n\n\n\n\n tettttttts5")
            messages.success(self.request, "Your order was successful")
            return redirect("/")
        except stripe.error.CardError as e:
        # Since it's a decline, stripe.error.CardError will be caught
            messages.error(self.request, f"{e.error.message}")
            return redirect("/")
        except stripe.error.RateLimitError as e:
        # Too many requests made to the API too quickly
            messages.error(self.request, "Rate Limit Error")
            return redirect("/")
        except stripe.error.InvalidRequestError as e:
        # Invalid parameters were supplied to Stripe's API
            print(e)
            messages.error(self.request, "Invalid Parameter")
            return redirect("/")
        except stripe.error.AuthenticationError as e:
        # Authentication with Stripe's API failed
        # (maybe you changed API keys recently)
            messages.error(self.request, "Not Authenticated")
            return redirect("/")
        except stripe.error.APIConnectionError as e:
        # Network communication with Stripe failed
            messages.error(self.request, " Network Error")
            return redirect("/")
        except stripe.error.StripeError as e:
        # Display a very generic error to the user, and maybe send
        # yourself an email
            messages.error(self.request, "Semothing went wrong. You are not charged. Please try again")
            return redirect("/")
        except Exception as e:
        # Something else happened, completely unrelated to Stripe 
            messages.error(self.request, "A serious error occured. We have been notified")
            return redirect("/")



class HomeView(ListView):
    model = Item
    context_object_name = 'Items'
    template_name = "home.html"
    paginate_by = 80


class ItemDetailView(DetailView):
    model = Item
    #context_object_name = "product"
    template_name = "product.html"


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")

        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect("core:order-summary")

    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect("core:order-summary")


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            messages.info(request, "This item was removed from your cart.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:order-summary")
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, "you do not have an active order")
            return redirect('/')


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)

