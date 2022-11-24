from django.urls import path
from api_v2.views import ProductView, OrderView, CheckoutView, pay, single_item_order_checkout, Success, Cancel, Decline

urlpatterns = [
    path('item/<int:pk>', ProductView.as_view(), name='product'),
    path('buy/<int:pk>', CheckoutView.as_view(), name='checkout'),
    path('order/<int:pk>', OrderView.as_view(), name='order'),
    path('buy/<int:pk>/pay', pay, name='pay'),
    path('success/', Success.as_view()),
    path('decline/', Decline.as_view()),
    path('cancel/', Cancel.as_view()),
    path('order/create_for/<int:pk>', single_item_order_checkout)
]

