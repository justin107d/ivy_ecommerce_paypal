import json
from .models import *


# stores cart data as a cookie and will create a cart if none exists
def cookie_cart(request):
    try:
            cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}

    print('Cart: ', cart)
    items = []
    order = {'get_cart_total':0,'get_cart_items':0,'shipping': False}
    cartItems = order['get_cart_items']

    for i in cart:
        try:
            cartItems += cart[i]['quantity']

            product = Product.objects.get(id=i)
            total = (product.price * cart[i]['quantity'])

            order['get_cart_total'] += total
            order['get_cart_items'] += cart[i]['quantity']

            item = {
                'product':{
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'imageURL': product.imageURL
                    },
                'quantity': cart[i]['quantity'],
                'get_total': total,
            }
            items.append(item)

            if product.digital == False:
                order['shipping'] = True
        except:
            pass

    return {'items': items, 'order': order, 'cartItems': cartItems}

#checks authentication and retrieved cart stored as a cookie
def cart_data(request):

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

    return {'items': items, 'order': order, 'cartItems': cartItems}

# process order for guests
def guest_order(request, data):
    
    print('User is not logged in...')

    print("COOKIES: ", request.COOKIES)
    name = data['form']['name']
    email = data['form']['email']
    
    cookieData = cookie_cart(request)
    items = cookieData['items']
    order = cookieData['order']
    cartItems = cookieData['cartItems']

    customer, created =Customer.objects.get_or_create(
        email=email,
    )
    customer.name = name
    customer.save()

    order = Order.objects.create(
        customer = customer,
        complete = False
        )

    for item in items:
        product = Product.objects.get(id=item['product']['id'])

        orderItem = OrderItem.objects.create(
            product = product,
            order = order,
            quantity = item['quantity']
        )
    
    return customer, order