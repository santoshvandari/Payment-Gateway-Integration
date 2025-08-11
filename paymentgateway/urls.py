from django.urls import path
from paymentgateway import views

urlpatterns = [
    path("order-list/", views.order_list, name="order_list"),
    path("order-checkout/<int:order_id>/", views.order_checkout, name="order_checkout"),
]
