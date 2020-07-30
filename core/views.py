from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.utils import timezone
from django.views.generic import ListView, DetailView, View
from .models import Item, OrderItem, Order, BillingAddress
from .forms import CheckoutForm
from django.conf import settings


class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, is_ordered=False)
            # form
            form = CheckoutForm()
            context = {
                'form': form
            }
            return render(self.request, "checkout.html", context)
        except ObjectDoesNotExist:
            return redirect("core:order-summary")

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, is_ordered=False)
            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                zip = form.cleaned_data.get('zip')
                # TODO: add functionality for these fields
                # same_shipping_address = form.cleaned_data.get(
                #     'same_shipping_address')
                # save_info = form.cleaned_data.get('save_info')
                payment_option = form.cleaned_data.get('payment_option')
                billing_address = BillingAddress(
                    user=self.request.user,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    country=country,
                    zip=zip,
                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()
                # TODO: add redirect to the selected payment option
                return redirect('core:checkout')
            messages.warning(self.request, "Failed checkout.")
            return render(self.request, "checkout.html", {'form': form})
        except ObjectDoesNotExist:
            # messages.info(self.request, "You do not have an active order.")
            return redirect("core:order-summary")

STRIPE_SECRET_KEY = "sk_test_4eC39HqLyjWDarjtT1zdp7dc"

import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

# `source` is obtained with Stripe.js; see https://stripe.com/docs/payments/accept-a-payment-charges#web-create-token



class PaymentView(View):
    def get(self, *args, **kwargs):
        # order
        return render(self.request, "payment.html")

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, is_ordered=False)
        token = self.request.POST.get('stripeToken')
        stripe.Charge.create(
            amount=order.get_total() * 100, #cents
            currency="eur",
            source=token,
        )

        order.is_ordered = True


def products(request):
    context = {'items': Item.objects.all()}
    return render(request, "products.html", context)


class HomeView(ListView):
    model = Item
    paginate_by = 8
    template_name = "home.html"


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, is_ordered=False)
            context = {
                'object': order,
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order.")
            return render(self.request, 'order_summary.html')


class ItemDetailView(DetailView):
    model = Item
    template_name = "product.html"


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        is_ordered=False,
    )
    order_qs = Order.objects.filter(user=request.user, is_ordered=False)
    if order_qs.exists():
        order = order_qs[0]
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
    order_qs = Order.objects.filter(user=request.user, is_ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order.
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                is_ordered=False,
            )[0]
            order_item.delete()
            messages.warning(request, "This item was removed from your cart.")
            if order.items.count() == 0:
                order.delete()
            return redirect("core:order-summary")
        else:
            messages.warning(request, "This item was not in your cart.")
            return redirect("core:product", slug=slug)
    else:
        messages.warning(request, "You do not have an active order.")
        return redirect("core:product", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, is_ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order.
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                is_ordered=False,
            )[0]
            if order_item.quantity >= 2:
                order_item.quantity -= 1
                order_item.save()
                messages.info(request, "This item quantity was updated.")
                return redirect("core:order-summary")
            else:
                order_item.delete()
                messages.warning(
                    request, "This item was removed from your cart.")
                if order.items.count() == 0:
                    order.delete()
                return redirect("core:order-summary")
        else:
            messages.warning(request, "This item was not in your cart.")
            return redirect("core:product", slug=slug)
    else:
        messages.warning(request, "You do not have an active order.")
        return redirect("core:product", slug=slug)
