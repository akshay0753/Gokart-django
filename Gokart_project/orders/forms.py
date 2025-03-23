from django import forms
from .models import Order

from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'first_name', 'last_name', 'phone', 'email', 
            'address_1', 'address_2', 'country', 'state', 'city', 
            'order_note'
        ]

        
        
        
    