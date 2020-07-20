from django.urls import path
from . import views

app_name = "core"
urlpatterns = [
    path('', views.HomeView.as_view(), name="homepage"),
    path('checkout/', views.checkout, name="checkout"),
    path('product/<slug>/', views.ItemDetailView.as_view(), name="product"),
    path('add-to-cart/<slug>/', views.add_to_cart, name="add-to-cart"),
    
]
