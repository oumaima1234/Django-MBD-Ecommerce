from django.urls import path
from .views import (
	HomeView, 
	ItemDetailView, 
	checkout, 
	add_to_chart,
	remove_from_cart
	)

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('product/<id>', ItemDetailView.as_view(), name='product'),
    path('checkout/', checkout, name='checkout'),
    path('add_to_chart/<id>', add_to_chart, name='add-to-chart'),
    path('remove-from-cart/<id>/', remove_from_cart, name='remove-from-cart'),

]
