from django import forms
from .models import Account

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'enter password here'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'enter password here'}))
    
    def __init__(self, *args, **kwrgs):
        super().__init__(*args,**kwrgs)
        for field in self.fields :
            self.fields[field].widget.attrs['class'] = 'form-control'
            self.fields[field].widget.attrs['placeholder'] = f'enter {field} here'
            
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password != confirm_password:
            raise forms.ValidationError('password does not match')
    
    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'password']
    
    
        
        
    
        