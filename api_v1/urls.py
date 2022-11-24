from django.urls import path
from api_v1.views import ItemView, create_checkout_session_for_item, Success, Cancel, OrderView, \
    create_checkout_session_for_order

urlpatterns = [
    path('item/<int:pk>', ItemView.as_view(), name='item'),
    path('buy/<int:pk>', create_checkout_session_for_item, name='buy'),
    path('success/', Success.as_view(), name='success'),
    path('cancel/', Cancel.as_view(), name='cancel'),
    path('order/<int:pk>', OrderView.as_view(), name='order'),
    path('order/<int:pk>/buy', create_checkout_session_for_order)
]

