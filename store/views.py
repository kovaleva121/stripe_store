import stripe
from django.conf import settings
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Item, Order


def get_stripe_keys(currency):
    """Возвращает ключи Stripe"""
    return settings.STRIPE_PUBLISHABLE_KEY, settings.STRIPE_SECRET_KEY


def item_detail(request, id):
    """HTML страница товара с кнопкой покупки"""
    item = get_object_or_404(Item, id=id)
    publishable_key, _ = get_stripe_keys(item.currency)

    context = {
        'item': item,
        'publishable_key': publishable_key,
    }
    return render(request, 'store/item_detail.html', context)


def order_detail(request, order_id):
    """HTML страница заказа с кнопкой покупки"""
    order = get_object_or_404(Order, id=order_id)
    order.calculate_total()

    # Используем валюту первого товара в заказе
    currency = order.items.first().currency if order.items.exists() else 'usd'
    publishable_key, _ = get_stripe_keys(currency)

    context = {
        'order': order,
        'publishable_key': publishable_key,
    }
    return render(request, 'store/order_detail.html', context)


@csrf_exempt
def create_checkout_session(request, id):
    """Создание Stripe Checkout Session для товара"""
    item = get_object_or_404(Item, id=id)
    _, secret_key = get_stripe_keys(item.currency)

    stripe.api_key = secret_key

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': item.currency,
                        'unit_amount': int(item.price * 100),  # cents
                        'product_data': {
                            'name': item.name,
                            'description': item.description,
                        },
                    },
                    'quantity': 1,
                }
            ],
            mode='payment',
            success_url=request.build_absolute_uri('/success/'),
            cancel_url=request.build_absolute_uri('/cancel/'),
        )
        return JsonResponse({'sessionId': checkout_session.id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
def create_order_checkout_session(request, order_id):
    """Создание Stripe Checkout Session для заказа"""
    order = get_object_or_404(Order, id=order_id)
    order.calculate_total()

    # Используем валюту первого товара в заказе
    currency = order.items.first().currency if order.items.exists() else 'usd'
    _, secret_key = get_stripe_keys(currency)

    stripe.api_key = secret_key

    try:
        line_items = []
        for item in order.items.all():
            line_items.append({
                'price_data': {
                    'currency': item.currency,
                    'unit_amount': int(item.price * 100),
                    'product_data': {
                        'name': item.name,
                        'description': item.description,
                    },
                },
                'quantity': 1,
            })

        checkout_data = {
            'payment_method_types': ['card'],
            'line_items': line_items,
            'mode': 'payment',
            'success_url': request.build_absolute_uri('/success/'),
            'cancel_url': request.build_absolute_uri('/cancel/'),
        }

        # Добавляем скидку если есть
        if order.discount and order.discount.stripe_coupon_id:
            checkout_data['discounts'] = [{
                'coupon': order.discount.stripe_coupon_id
            }]

        checkout_session = stripe.checkout.Session.create(**checkout_data)
        return JsonResponse({'sessionId': checkout_session.id})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# Бонус: Payment Intent вместо Session
@csrf_exempt
def create_payment_intent(request, id):
    """Создание Stripe Payment Intent (бонусная задача)"""
    item = get_object_or_404(Item, id=id)
    _, secret_key = get_stripe_keys(item.currency)

    stripe.api_key = secret_key

    try:
        intent = stripe.PaymentIntent.create(
            amount=int(item.price * 100),
            currency=item.currency,
            metadata={'item_id': item.id},
        )
        return JsonResponse({
            'clientSecret': intent.client_secret,
            'publishableKey': get_stripe_keys(item.currency)[0]
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
