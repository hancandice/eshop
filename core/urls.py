from django.urls import path
from . import views

app_name = "core"
urlpatterns = [
    path('', views.homepage, name="homepage"),
    path('checkout/', views.checkout, name="checkout"),
    path('products/', views.products, name="products"),
]
