from django import forms
from .models import Transaction 
from accounts.models import UserBankAccounts

class TransactionForm(forms.ModelForm):
    class Meta:
        model=Transaction
        fields=['amount','transaction_type']
        
    def __init__(self,*args,**kwargs):
        self.account=kwargs.pop('account',None) #keyword argument a views theke user account er object ti account e kre pathano hoise
        super().__init__(*args,**kwargs)
        self.fields['transaction_type'].disabled=True   #ei field disable thakbe
        self.fields['transaction_type'].widget=forms.HiddenInput   # user er theke hide rekhe input dibe backend theke
        
    def save(self,commit=True):
        self.instance.account=self.account
        self.instance.balance_after_transaction=self.account.balance
        return super().save()  #Calls the original save() method from the parent class. Ensures the updated instance is saved in the database.Returns the saved instance.
    
class DepositeForm(TransactionForm):
    def clean_amount(self): #clean built in method ar amount field ke filter,update korbo
        min_deposite_amount=100
        amount=self.cleaned_data.get('amount')
        if amount < min_deposite_amount:
            raise forms.ValidationError(
                f'Your minimum deposite amount should be {min_deposite_amount}$'
            )
        return amount

class WithdrawForm(TransactionForm):
    
    
    
    def __init__(self, *args, **kwargs):
        self.bankrupt=kwargs.pop('bankrupt')
        super().__init__(*args, **kwargs)
    
    def clean_amount(self):
        account=self.account    
        min_withdraw_amount=500
        max_withdraw_amount=20000
        balance=account.balance
        amount=self.cleaned_data.get('amount')
        print(self.bankrupt)
        if  self.bankrupt == False:
        
            if  amount < min_withdraw_amount:
                raise forms.ValidationError(
                    f'You have to withdraw at least {min_withdraw_amount}$'
                
                )
            if amount >max_withdraw_amount:
                raise forms.ValidationError(
                    f'You can withdraw at most {max_withdraw_amount}$'
                )
            
            if amount > balance:
                raise forms.ValidationError(
                    f'You have  {balance}$ in your account'
                )
        else:
            raise forms.ValidationError(
                f"This bank is bankrupted cannot withdraw money"
            )
        return amount
class LoanRequestForm(TransactionForm):
    def clean_amount(self):
        amount=self.cleaned_data.get('amount')
        
        return amount
    
class FundTransferForm(TransactionForm):
    receiver_ac=forms.CharField(max_length=100,label="Receiver's Account Number")
    class Meta:
        model=Transaction
        fields=['receiver_ac','amount','transaction_type']
        
    # def __init__(self,*args,**kwargs):
    #     self.account=kwargs.pop('account',None) #keyword argument a views theke user account er object ti account e kre pathano hoise
    #     super().__init__(*args,**kwargs)
    #     self.fields['transaction_type'].disabled=True   #ei field disable thakbe
    #     self.fields['transaction_type'].widget=forms.HiddenInput
        
    #     if self.account:
    #         self.instance.account=self.account
    
    def clean_amount(self):
        receiver_account_number = self.cleaned_data.get('receiver_ac')
        amount=self.cleaned_data.get('amount')
        try:
            receiver_account = UserBankAccounts.objects.get(account_no=receiver_account_number)
        except UserBankAccounts.DoesNotExist:
            raise forms.ValidationError('The receiver account does not exist.')
        self.cleaned_data['receiver_account'] = receiver_account
        return amount

        
        