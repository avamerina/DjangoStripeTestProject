from django.shortcuts import redirect
import stripe
from django.conf import settings
from django.urls import reverse
from django.views.generic import TemplateView

from api_v1.models import Item


class ItemView(TemplateView):
    template_name = 'api_v1/item.html'

    def get_context_data(self, **kwargs):
        item = Item.objects.get(pk=self.kwargs['pk'])
        context = super().get_context_data(**kwargs)
        context['item'] = item
        return context


class Success(TemplateView):
    template_name = 'api_v1/success.html'


class Cancel(TemplateView):
    template_name = 'api_v1/cancel.html'


def create_checkout_session(request, pk):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    item = Item.objects.get(pk=pk)
    session = stripe.checkout.Session.create(
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': item.name,
                },
                'unit_amount': int(item.price*100),
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=request.build_absolute_uri(reverse('success')) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=request.build_absolute_uri(reverse('cancel')),
    )

    return redirect(session.url, code=303)

