from django.shortcuts import redirect
import stripe
from django.conf import settings
from django.urls import reverse
from django.views.generic import TemplateView

from api_v1.models import Item, Order


class ItemView(TemplateView):
    template_name = 'api_v1/item.html'

    def get_context_data(self, **kwargs):
        item = Item.objects.get(pk=self.kwargs['pk'])
        context = super().get_context_data(**kwargs)
        context['item'] = item
        return context


class OrderView(TemplateView):
    template_name = 'api_v1/order.html'

    @staticmethod
    def get_total_amount(order_id):
        order = Order.objects.get(pk=order_id)
        total = 0
        for i in order.items.all():
            total += i.price
        return total

    def get_context_data(self, **kwargs):
        order = Order.objects.get(pk=self.kwargs['pk'])
        context = super().get_context_data(**kwargs)
        context['order'] = order
        context['total_amount'] = self.get_total_amount(order.id)
        return context


class Success(TemplateView):
    template_name = 'api_v1/success.html'


class Cancel(TemplateView):
    template_name = 'api_v1/cancel.html'


def create_checkout_session_for_item(request, pk):
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


def create_line_item_list(order_id, tax):
    order = Order.objects.get(pk=order_id)
    line_item_list = []
    for item in order.items.all():
        line_item_list.append(
            {
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': item.name,
                    },
                    'unit_amount': int(item.price * 100),
                },
                'quantity': 1,
                'tax_rates': [tax.id]
            }
        )
    return line_item_list


def create_checkout_session_for_order(request, pk):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    order = Order.objects.get(pk=pk)

    tax = stripe.TaxRate.create(
        display_name="Sales Tax",
        inclusive=False,
        percentage=order.tax,
        country="US",
        state="CA",
        jurisdiction="US - CA",
        description="CA Sales Tax",
    )
    if order.discount:
        discount = stripe.Coupon.create(
            percent_off=order.discount,
        )

    session = stripe.checkout.Session.create(
        line_items=create_line_item_list(pk, tax),
        mode='payment',
        discounts=[{
            'coupon': discount.id,
        }],
        success_url=request.build_absolute_uri(reverse('success')) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=request.build_absolute_uri(reverse('cancel')),
    )

    return redirect(session.url, code=303)

