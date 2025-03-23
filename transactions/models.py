from django.db import models
from accounts.models import UserBankAccounts
from .constants import TRANSACTION_TYPE
# Create your models here.

class Transaction(models.Model):
    #all transaction related database will be created here like deposite (account balance+),withdrawl(account balance -),loan (account balance +),we will try to do all of this tasks to do in one model
    account=models.ForeignKey(UserBankAccounts,related_name='transactions',on_delete=models.CASCADE)
    amount=models.DecimalField(decimal_places=2,max_digits=12)
    balance_after_transaction=models.DecimalField(decimal_places=2,max_digits=12)
    transaction_type=models.IntegerField(choices=TRANSACTION_TYPE,null=True)
    timestamp=models.DateTimeField(auto_now_add=True)
    loan_approve=models.BooleanField(default=False)
    bankrupt=models.BooleanField(default=False)
    
    class Meta:
        ordering=['timestamp']
    
