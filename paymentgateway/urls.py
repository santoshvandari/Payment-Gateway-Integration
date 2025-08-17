from django.urls import path
from paymentgateway import views

urlpatterns = [
    path("", views.order_list, name="order_list"),
    path("order-list/", views.order_list, name="order_list"),
    path("order-checkout/<int:order_id>/", views.order_checkout, name="order_checkout"),
    path("order-success/<int:order_id>/", views.order_success, name="order_success"),
    
    # eSewa URLs
    path("esewa-success/", views.esewa_success, name="esewa_success"),
    path("esewa-failure/", views.esewa_failure, name="esewa_failure"),
    
    # Khalti URLs
    path("khalti-success/", views.khalti_success, name="khalti_success"),
    path("khalti-failure/", views.khalti_failure, name="khalti_failure"),
    path("khalti-webhook/", views.khalti_webhook, name="khalti_webhook"),
    
    # API URLs
    path("payment-status/<int:order_id>/", views.PaymentStatusView.as_view(), name="payment_status"),
    
    # Test order creation
    path("create-test-order/", views.create_test_order, name="create_test_order"),
]
