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
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)

                    # Getting the product variations by cart id
                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                    # Get the cart items from the user to access his product variations
                    cart_item = CartItem.objects.filter(user=user)
                    ex_var_list = []
                    id = []
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)

                    # product_variation = [1, 2, 3, 4, 6]
                    # ex_var_list = [4, 6, 3, 5]

                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()
            except:
                pass
            auth.login(request, user)
            messages.success(request, 'You are now logged in.')
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                # next=/cart/checkout/
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')
    return render(request, 'accounts/login.html')


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