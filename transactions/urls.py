
from django.urls import path
from .views import DepositeMoneyView,WithdrawMoneyView,LoanRequestView,TransactionReportView,PayloanView,LoanListView,FundTransferView

urlpatterns = [
    path("deposite/",DepositeMoneyView.as_view(),name='deposite_money'),
    path("withdraw/",WithdrawMoneyView.as_view(),name='withdraw_money'),
    path("report/",TransactionReportView.as_view(),name='transaction_report'),
    path("loan_request/",LoanRequestView.as_view(),name='loan_request'),
    path("loans/",LoanListView .as_view(),name='loan_list'),
    path("loans/<int:loan_id>/",PayloanView.as_view(),name='pay_loan'),
    path("transfer/",FundTransferView.as_view(),name='fund_transfer')

]