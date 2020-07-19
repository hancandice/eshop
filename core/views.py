from django.shortcuts import render
from .models import Item


def homepage(request):
    context = {'items': Item.objects.all()}
    return render(request, "home-page.html", context)


def checkout(request):
    context = {'items': Item.objects.all()}
    return render(request, "checkout-page.html", context)


def products(request):
    context = {'items': Item.objects.all()}
    return render(request, "product-page.html", context)
