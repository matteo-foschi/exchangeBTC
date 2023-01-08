from django.contrib import admin
from .models import Order
from .models import Profile
admin.site.register(Profile)
admin.site.register(Order)
# Register your models here.
