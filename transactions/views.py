from django.shortcuts import render
from django.views.generic import CreateView,ListView,FormView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Transaction
from .forms import DepositeForm,WithdrawForm,LoanRequestForm,FundTransferForm
from .constants import DEPOSITE,WITHDRAWL,LOAN,LOAN_PAID,TRANSFER
from django.contrib import messages
from django.http import HttpResponse
from datetime import datetime
from django.db.models import Sum
from django.shortcuts import get_object_or_404,redirect
from django.urls import reverse_lazy
from django.core.mail import EmailMessage,EmailMultiAlternatives
from django.template.loader import render_to_string



def send_transaction_email(user,amount,subject,template):
    message= render_to_string(template,{'user':user,'amount':amount})
    send_email=EmailMultiAlternatives(subject,message,to=[user.email])
    send_email.attach_alternative(message,"text/html")
    send_email.send()

# Create your views here.
#ei view ke inherit kore amra deposite ,withdraw,loan request er kaj korbo
class TransactionCreateMixin(LoginRequiredMixin,CreateView):
    template_name='./transactions/transaction_form.html'
    model=Transaction
    title=''
    success_url=reverse_lazy('transaction_report')
    
    def get_form_kwargs(self):
        kwargs=super().get_form_kwargs()
        kwargs.update({
            'account':self.request.user.account
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        context.update({
            'title':self.title
        })
        return context
    
class DepositeMoneyView(TransactionCreateMixin):
    form_class=DepositeForm
    title='Deposite'
    
    def get_initial(self):
        initial={'transaction_type':DEPOSITE}
        return initial
    
    def form_valid(self,form):
        amount=form.cleaned_data.get('amount')
        account=self.request.user.account
        account.balance += amount
        account.save (
            update_fields=['balance']
        )
        messages.success(self.request,f"{amount}$ was deposited to your account")
        # mail_subject = 'Deposite Message'
        # message= render_to_string('transactions/deposite_email.html',{'user':self.request.user,'amount':amount})
        # to_mail=self.request.user.email
        # send_email=EmailMultiAlternatives(mail_subject,message,to=[to_mail])
        # send_email.attach_alternative(message,"text/html")
        # send_email.send()
        send_transaction_email(self.request.user,amount,"Deposite Message",'transactions/deposite_email.html')
        return super().form_valid(form )
            
class WithdrawMoneyView(TransactionCreateMixin):
    form_class=WithdrawForm
    title='Withdraw'
    
    def get_initial(self):
        initial={'transaction_type':WITHDRAWL}
        return initial
    
    #bankruptcy code added here
    def get_bankrupt_status(self):
        account=self.request.user.account
        last_transaction=Transaction.objects.filter(account=account).order_by('-timestamp').first()
        # print(last_transaction.bankrupt)
        last_transaction.refresh_from_db()
        # print(Transaction.objects.values('id', 'bankrupt'))
        # last_transaction.bankrupt=True
        return  last_transaction.bankrupt 
    
    def get_form_kwargs(self):
        kwargs= super().get_form_kwargs()
        kwargs['bankrupt']=self.get_bankrupt_status()
        return kwargs
    
    
    
    
    def form_valid(self,form):
        amount=form.cleaned_data.get('amount')
        account=self.request.user.account
        account.balance -= amount
        account.save (
            update_fields=['balance']
        )
        messages.success(self.request,f"Successfully withdrawn {amount}$ from your account")
        send_transaction_email(self.request.user,amount,"Withdrawal Message",'transactions/withdrawal.html')
        return super().form_valid(form )
    

class LoanRequestView(TransactionCreateMixin):
    form_class=LoanRequestForm
    title='Request For Loan'
    
    def get_initial(self):
        initial={'transaction_type':LOAN}
        return initial
    
    def form_valid(self,form):
        amount=form.cleaned_data.get('amount')
        current_loan_count=Transaction.objects.filter(account=self.request.user.account,transaction_type=LOAN,loan_approve=True).count()
        if current_loan_count>=3:
            return HttpResponse( "You cannot have more than 3 active loans at a time.")
        messages.success(self.request,f"Loan request for {amount}$ has been sent successfully")
        send_transaction_email(self.request.user,amount,"Loan Request Message",'transactions/loan.html')
        return super().form_valid(form )
    
    
#form er kaj form e model er kaj views e korte hoi

class TransactionReportView(LoginRequiredMixin,ListView):
    template_name='transactions/transaction_report.html'
    model=Transaction   
    balance=0
    
    def get_queryset(self):
        queryset=super().get_queryset().filter(
            account=self.request.user.account
        )
        start_date_str=self.request.GET.get('start_date')
        end_date_str=self.request.GET.get('end_date')
        
        if start_date_str and end_date_str:
            start_date=datetime.strptime(start_date_str,"%Y-%m-%d").date()
            end_date=datetime.strptime(end_date_str,"%Y-%m-%d").date()
            
            queryset = queryset.filter(timestamp__date__gte = start_date, timestamp__date__lte = end_date)
            self.balance=Transaction.objects.filter(timestamp__date__gte = start_date, timestamp__date__lte = end_date).aggregate(Sum('amount'))['amount__sum']
            
        else:
            self.balance =self.request.user.account.balance
        
        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        context.update({
            'account' : self.request.user.account
        })
        return context
    
class PayloanView(LoginRequiredMixin,View):
    def get(self,request,loan_id):
        loan=get_object_or_404(Transaction,id=loan_id)
        
        if loan.loan_approve:
            user_account=loan.account
            if loan.amount < user_account.balance:
                user_account.balance -= loan.amount
                loan.balance_after_transaction = user_account.balance
                user_account.save()
                loan.transaction_type=LOAN_PAID 
                loan.save()
                return redirect('loan_list')
            else:
                messages.error(self.request,f"Loan amount is greater than available balance")
                return redirect('loan_list')
            
            
class LoanListView(LoginRequiredMixin,ListView):
    model=Transaction
    template_name='transactions/loan_request.html'
    context_object_name='loans'
    
    def get_queryset(self):
        user_account=self.request.user.account  
        queryset=Transaction.objects.filter(account=user_account,transaction_type=LOAN)
        return queryset
    
class FundTransferView(TransactionCreateMixin):
    model=Transaction
    form_class=FundTransferForm
    title='Fund Transfer'
    success_url=reverse_lazy('transaction_report')
    
    def get_initial(self):
        return{'transaction_type':TRANSFER}
    
    def form_valid(self, form):
        user_account = self.request.user.account
        receiver_account = form.cleaned_data.get('receiver_account')
        amount = form.cleaned_data.get('amount')
        print(amount)

        if user_account.balance >= amount:
            user_account.balance -= amount
            receiver_account.balance += amount
            user_account.save(update_fields=['balance'])
            receiver_account.save(update_fields=['balance'])
#for self.request.user.account
            Transaction.objects.create(
                account=user_account,
                transaction_type=TRANSFER,
                amount=-amount,
                balance_after_transaction=user_account.balance
            )
#for receiver account
            Transaction.objects.create(
                account=receiver_account,
                transaction_type=TRANSFER,
                amount=amount,
                balance_after_transaction=receiver_account.balance
            )

            messages.success(self.request, f"Successfully transferred {amount}$ to {receiver_account.user.username}")
            return super().form_valid(form)
        else:
            form.add_error(None, "Insufficient balance")
            return self.form_invalid(form)