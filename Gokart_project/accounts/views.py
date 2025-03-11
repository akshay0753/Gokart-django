from django.shortcuts import render, redirect
from .models import Account
from .forms import RegistrationForm
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from carts.views import _cart_id
from carts.models import CartItem, Cart
#Verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
import requests
import urllib.parse
# Create your views here.
def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            username = email.split('@')[0]
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email,
                                               username=username, password=password)
            user.phone_number=phone_number
            user.save()
            # user activation
            current_site = get_current_site(request)
            mail_subject = "Please activate your account"
            message = render_to_string('accounts/account_verification_email.html', {
                        'user': user,
                        'domain': current_site.domain,  # Ensure you use `.domain`
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),  # Use `uidb64` instead of `uid`
                        'token': default_token_generator.make_token(user)
                    })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            # messages.success(request,"Thank You for Registration with us. we have sent you a verification email to your email address, PLease verify it.....!")
            return redirect('/accounts/login/?command=verification&email='+email)
        else:
            context = {
                'form': form
            }
            return render(request, "accounts/register.html", context)
            
            
    form = RegistrationForm()
    context = {
        'form': form
    }
    return render(request, "accounts/register.html", context)

from django.shortcuts import render, redirect
from django.contrib import messages, auth
from carts.models import Cart, CartItem
from carts.views import _cart_id

def login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = auth.authenticate(email=email, password=password)  # Ensure custom user model supports email auth
        
        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                cart_items = CartItem.objects.filter(cart=cart)

                if cart_items.exists():
                    # Getting the product variations by cart id
                    product_variation_list = [list(item.variation.all()) for item in cart_items]

                    # Get the cart items from user to access his product variations.
                    user_cart_items = CartItem.objects.filter(user=user)
                    existing_variation_list = [list(item.variation.all()) for item in user_cart_items]
                    item_id_map = {item.id: variations for item, variations in zip(user_cart_items, existing_variation_list)}

                    for variations in product_variation_list:
                        if variations in existing_variation_list:
                            item_id = list(item_id_map.keys())[existing_variation_list.index(variations)]
                            existing_item = CartItem.objects.get(id=item_id)
                            existing_item.quantity += 1
                            existing_item.user = user
                            existing_item.save()
                        else:
                            for item in cart_items:
                                item.user = user
                                item.save()

            except Cart.DoesNotExist:
                pass  # Log this if necessary

            auth.login(request, user)
            messages.success(request, "You are now logged in.")
            url = request.META.get('HTTP_REFERER')
            if url:
                parsed_url = urllib.parse.urlparse(url)
                query_params = urllib.parse.parse_qs(parsed_url.query)  # Properly parse query parameters

                if 'next' in query_params:
                    next_page = query_params['next'][0]  # Extract the first value
                    return redirect(next_page)

    else:
        messages.error(request, "Invalid credentials")
        return redirect('login')        

    return render(request, "accounts/login.html")


@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, "Your successfully Logout....!")
    return redirect('login')

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, OverflowError, Account.DoesNotExist):
        user=None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations...! Your account is activated....!')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation Link')
        return redirect('register')
  
  
   
@login_required(login_url='login') 
def dashboard(request):
    return render(request,'accounts/dashboard.html')
    
def forgotpassword(request):
    if request.method == "POST":
        email = request.POST.get('email')
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)
            current_site = get_current_site(request)
            mail_subject = "Reset Your Password"
            message = render_to_string('accounts/reset_password_email.html', {
                        'user': user,
                        'domain': current_site.domain,  # Ensure you use `.domain`
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),  # Use `uidb64` instead of `uid`
                        'token': default_token_generator.make_token(user)
                    })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            messages.success(request,"Your Reset password Request send to your mail successfully please check....!")
            return redirect('login')
        else:
            messages.error(request, 'Accounts does not exist Register first...!')
            return redirect('forgotpassword')
    return render(request,'accounts/forgotpassword.html')

def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, OverflowError, Account.DoesNotExist):
        user=None
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('resetpassword')
    else:
        messages.error(request, 'this link has been expired')
        return redirect('login')
    
        

    
def resetpassword(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password == confirm_password:
            uid = request.session.get('uid')  # ✅ Get UID properly from session
            if uid:
                try:
                    user = Account.objects.get(id=uid)  # ✅ Fetch user safely
                    user.set_password(password)
                    user.save()
                    messages.success(request, 'Password reset Successfully')
                    return redirect('login')
                except Account.DoesNotExist:
                    messages.error(request, 'Invalid user session.')
                    return redirect('forgotpassword')
            else:
                messages.error(request, 'Session expired. Try resetting again.')
                return redirect('login')
        else:
            messages.error(request, 'Passwords do not match!')
            return redirect('resetpassword')

    return render(request, 'accounts/resetpassword.html')