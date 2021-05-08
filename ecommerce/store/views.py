from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import datetime

from .models import *
from .utils import cookie_cart, cart_data, guest_order

# variables must be in all sections in order to be pulled into header

def store(request):
        
    data = cart_data(request)
    cartItems = data['cartItems']
    
    products = Product.objects.all()
    context={'products':products, 'cartItems': cartItems}
    return render(request, 'store/store.html', context)

def cart(request):

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        # .orderitem_set.all() is sort of a reverse lookup that grabs all the orderitem classes associated 
        # to this particular Order class referenced above.
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        cookieData = cookie_cart(request)
        items = cookieData['items']
        order = cookieData['order']
        cartItems = cookieData['cartItems']

    context={'items': items, 'order': order, 'cartItems': cartItems}

    return render(request, 'store/cart.html', context)

def checkout(request):
    
    data = cookie_cart(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']

    context={'items':items, 'order':order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)

def update_item(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print(' ')
    print('Action: ', action)
    print('ProductId: ', productId)

    customer = request.user.customer
    # These are loaded from models.py
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
    
    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)

@csrf_exempt #there is a video on a potential better solution to this
def process_order(request):
    transaction_id = datetime.datetime.now().timestamp()
    print('request body: ', request.body)
    data = json.loads(request.body)


    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

    else:
        customer, order = guest_order(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping == True:
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address = data['shipping']['address'],
                city=data['shipping']['city'],
                state=data['shipping']['state'],
                zipcode=data['shipping']['zipcode']
            )

    return JsonResponse('Payment complete!', safe=False)