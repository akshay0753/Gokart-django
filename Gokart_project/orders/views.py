from django.shortcuts import render, redirect
from django.http import HttpResponse
from carts.models import CartItem
from .forms import OrderForm
from .models import Order, OrderProduct, Payment
from datetime import datetime
import json

def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])
    payment = Payment(user = request.user,
                      payment_id = body['transID'],
                      payment_method = body['payment_method'],
                      amount_paid = order.order_total,
                      status = body['status']
                      )
    payment.save()
    order.payment = payment
    order.is_ordered = True
    
    # move cart item to ordered product table
    #  Reduce the queantity of sold products
    #  clear cart
    # Send order recieved email to customer
    # Send order number and transaction id back to here
    
    
    
    return render(request,'orders/payments.html')


def place_order(request):
    print("check1")
    current_user = request.user

    # Check if cart is empty
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    total = 0
    grand_total = 0
    tax = 0

    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)

    tax = (2 * total) / 100
    grand_total = total + tax
    print("check2")

    if request.method == "POST":
        form = OrderForm(request.POST)
        print("check3")

        if form.is_valid():
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_1 = form.cleaned_data['address_1']
            data.address_2 = form.cleaned_data.get('address_2', '')  # Optional field
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data.get('order_note', '')  # Optional field
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            
        
            
            # Generate order number
            current_date = datetime.today().strftime('%Y%m%d')
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()
            order = Order.objects.get(user=current_user, is_ordered =False, order_number=order_number)
            context = {
                'order':order,
                'cart_items' :cart_items,
                'total' : total,
                'tax' : tax,
                'grand_total':grand_total
            }
        
            return render(request,'orders/payments.html', context)  # Redirect to success page

        else:
            print("Form is invalid:", form.errors)  # Debugging invalid form cases
            return render(request, "store/checkout.html", {"form": form})  # Show errors in the form

    return redirect('store')  # If not a POST request, redirect to store


