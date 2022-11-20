from django.urls import path
from api_v1.views import ItemView, create_checkout_session, Success, Cancel

urlpatterns = [
    path('item/<int:pk>', ItemView.as_view(), name='item'),
    path('buy/<int:pk>', create_checkout_session, name='buy'),
    path('success/', Success.as_view(), name='success'),
    path('cancel/', Cancel.as_view(), name='cancel'),
]

