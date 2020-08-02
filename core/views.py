import stripe
from django.core.paginator import Paginator
from django.db.models import Q
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import DetailView, View
from .models import Item, OrderItem, Order, BillingAddress, Payment, Coupon
from .forms import CheckoutForm, CouponForm

stripe.api_key = settings.STRIPE_SECRET_KEY
STRIPE_PUBLIC_KEY = settings.STRIPE_PUBLISHABLE_KEY


def index(request):
    page = request.GET.get('page', '1')
    kw = request.GET.get('kw', '')
    sort = request.GET.get('sort', 'all')

    if sort == "starters":
        item_list = Item.objects.order_by(
            '-create_date').filter(category="Starters")
    elif sort == "main-dishes":
        item_list = Item.objects.order_by(
            '-create_date').filter(category="Main dishes")
    elif sort == "desserts":
        item_list = Item.objects.order_by(
            '-create_date').filter(category="Desserts")
    elif sort == "drinks":
        item_list = Item.objects.order_by(
            '-create_date').filter(category="Drinks")
    else:
        item_list = Item.objects.order_by('-create_date')
    if kw:
        item_list = item_list.filter(
            Q(title__icontains=kw) |
            Q(label__icontains=kw) |
            Q(description__icontains=kw)
        ).distinct()
    paginator = Paginator(item_list, 8)
    page_obj = paginator.get_page(page)
    context = {'page_obj': page_obj, 'page': page, 'kw': kw, 'sort': sort}
    return render(request, 'home.html', context)


class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, is_ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True,
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
                billing_address = BillingAddress(
                    user=self.request.user,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    country=country,
                    zip=zip,
                )
                billing_address.save()
                order.billing_address = billing_address
                payment_option = form.cleaned_data.get('payment_option')
                order.payment_option = payment_option
                order.save()

                if payment_option == "Stripe":
                    return redirect('core:payment', payment_option="stripe")
                elif payment_option == "PayPal":
                    return redirect('core:payment', payment_option="paypal")
                else:
                    messages.warning(
                        self.request, "Invalid payment option selected.")
                    return redirect("core:checkout")
            else:
                messages.warning(self.request, "Failed checkout.")
                context = {
                    'form': form,
                    'order': order,
                    'couponform': CouponForm()
                }
                return render(self.request, "checkout.html", context)
        except ObjectDoesNotExist:
            return redirect("core:order-summary")


class PaymentView(View):
    def get(self, request, payment_option, *args, **kwargs):
        if payment_option == "stripe":
            payment_option = "Stripe"
        elif payment_option == "paypal":
            payment_option = "PayPal"
        # order
        order = Order.objects.get(
            user=self.request.user, is_ordered=False, payment_option=payment_option)
        if order.billing_address:
            context = {
                'order': order,
                'DISPLAY_COUPON_FORM': False,
            }
            return render(self.request, "payment.html", context)
        else:
            messages.warning(
                self.request, "You have not added a billing address.")
            return redirect("core:checkout")

    def post(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, is_ordered=False)
            token = self.request.POST.get('stripeToken')
            amount = int(order.get_total() * 100)  # cents
            charge = stripe.Charge.create(
                amount=amount,
                currency="usd",
                source=token,
            )
            # Create the payment
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

            # assign the payment to the order

            order.is_ordered = True
            order.payment = payment
            order.save()

            order_items = order.items.all()
            order_items.update(is_ordered=True)
            for item in order_items:
                item.save()

            messages.success(
                self.request, "Your order was successful.")
            return redirect("/")

        except stripe.error.CardError as e:
            body = e.json_body
            err = body.get('error', {})
            messages.warning(self.request, f"{err.get('message')}")
            return redirect("/")
        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.warning(self.request, "Rate limit error")
            return redirect("/")
        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            messages.warning(self.request, "Invalid parameters")
            return redirect("/")
        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.warning(self.request, "Not authenticated")
            return redirect("/")
        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.warning(self.request, "Network error")
            return redirect("/")
        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.warning(
                self.request, "Something went wrong. You were not charged. Please try again.")
            return redirect("/")
        except Exception as e:
            # Something else happened, completely unrelated to Stripe
            # Send an email to me.
            messages.warning(
                self.request, "A serious error occurred. We have been notified.")
            return redirect("/")
        except ObjectDoesNotExist:
            return redirect("core:order-summary")


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


def products(request):
    context = {'items': Item.objects.all()}
    return render(request, "products.html", context)


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
            messages.success(request, "This item was added to your cart.")
            return redirect("core:order-summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.success(request, "This item was added to your cart.")
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


class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            code = form.cleaned_data.get('code')
            order = Order.objects.get(user=self.request.user, is_ordered=False)
            if order:
                try:
                    coupon = Coupon.objects.get(code=code)
                except ObjectDoesNotExist:
                    messages.warning(
                        self.request, "This coupon does not exist.")
                    return redirect("core:checkout")
                order.coupon = coupon
                order.save()
                messages.success(self.request, "Successfully added coupon.")
                return redirect("core:checkout")
            else:
                messages.warning(
                    self.request, "You do not have an active order.")
                return redirect("core:order-summary")
