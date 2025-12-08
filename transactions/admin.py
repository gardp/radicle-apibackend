from django.contrib import admin
from .models import Order, OrderItem, Payment, Receipt, Buyer   
# Register your models here.
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Payment)
admin.site.register(Receipt)
admin.site.register(Buyer)