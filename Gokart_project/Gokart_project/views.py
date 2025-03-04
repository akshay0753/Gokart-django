from django.http import HttpResponse
from django.shortcuts import render
from store.models import Product

def home(request):
    all_products = Product.objects.all().filter(is_available=True)
    return render(request,"home.html", {"products":all_products})