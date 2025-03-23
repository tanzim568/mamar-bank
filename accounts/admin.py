from django.contrib import admin
from .models import UserBankAccounts,UserAddress
# Register your models here.
admin.site.register(UserBankAccounts)
admin.site.register(UserAddress)