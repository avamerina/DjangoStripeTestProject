import json
import sqlite3
import stripe
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.generic import TemplateView
from api_v2.models import Product, Order
from core import settings


class ProductView(TemplateView):
    template_name = 'api_v2/product.html'

    def get_context_data(self, **kwargs):
        product = Product.objects.get(pk=self.kwargs['pk'])
        context = super().get_context_data(**kwargs)
        context['product'] = product
        return context


class OrderView(TemplateView):
    template_name = 'api_v2/order.html'

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


class CheckoutView(TemplateView):
    template_name = 'api_v2/checkout.html'

    def get_context_data(self, **kwargs):
        order = Order.objects.get(pk=self.kwargs['pk'])
        context = super().get_context_data(**kwargs)
        context['order'] = order
        return context


def single_item_order_checkout(request, pk):
    """Creates order directly from item if customer wish to checkout immediately"""
    last_order = Order.objects.all().last()
    current_order_id = last_order.id + 1
    connection = sqlite3.connect('db.sqlite3')
    cursor = connection.cursor()
    order_create = "INSERT INTO api_v2_order (id) values (?);"
    order_item = "INSERT INTO api_v2_order_items (order_id, product_id) values (?, ?);"
    cursor.execute(order_create, (current_order_id,))
    cursor.execute(order_item, (current_order_id, pk,))
    connection.commit()
    connection.close()
    return redirect('order', pk=current_order_id)


@csrf_exempt
def pay(request, pk):
    """AJAX endpoint when `/pay` is called from client"""
    data = json.loads(request.body.decode())
    intent = None
    total_amount = OrderView.get_total_amount(pk)
    stripe.api_key = settings.STRIPE_SECRET_KEY

    try:
        if 'payment_method_id' in data.keys():
            # Create the PaymentIntent
            intent = stripe.PaymentIntent.create(
                payment_method=data['payment_method_id'],
                amount=int(total_amount*100),
                currency='usd',
                confirmation_method='manual',
                confirm=True,
            )
        elif 'payment_intent_id' in data.keys():
            intent = stripe.PaymentIntent.confirm(data['payment_intent_id'])
        else:
            print('else')
    except stripe.error.CardError as e:
        # Display error on client
        return JsonResponse({'error': e.user_message})

    return generate_response(intent)


def generate_response(intent):
    """Note that if your API version is before 2019-02-11, 'requires_action' appears as 'requires_source_action'"""
    if intent.status == 'requires_action' and intent.next_action.type == 'use_stripe_sdk':
        # Tell the client to handle the action
        return JsonResponse({
          'requires_action': True,
          'payment_intent_client_secret': intent.client_secret,
          'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY
        })
    elif intent.status == 'succeeded':
        # The payment didn’t need any additional actions and completed!
        # Handle post-payment fulfillment
        return JsonResponse({'success': True})
    else:
        # Invalid status
        return JsonResponse({'error': 'Invalid PaymentIntent status'})


class Success(TemplateView):
    template_name = 'api_v2/success.html'


class Cancel(TemplateView):
    template_name = 'api_v2/cancel.html'


class Decline(TemplateView):
    template_name = 'api_v2/decline.html'
