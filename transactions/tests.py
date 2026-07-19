from decimal import Decimal
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from accounts.models import UserBankAccounts
from transactions.views import WithdrawMoneyView


class WithdrawViewRegressionTests(TestCase):
    def test_get_bankrupt_status_handles_accounts_without_transaction_history(self):
        user = User.objects.create_user(username='withdraw-user', password='secret123')
        account = UserBankAccounts.objects.create(
            user=user,
            account_no=123456,
            account_type='Savings',
            gender='Male',
            balance=Decimal('1000.00'),
        )

        view = WithdrawMoneyView()
        view.request = type('Req', (), {'user': type('UserStub', (), {'account': account})()})()

        self.assertIs(view.get_bankrupt_status(), False)


class DepositFlowRegressionTests(TestCase):
    def test_deposit_posts_update_balance_and_redirect(self):
        user = User.objects.create_user(username='deposit-user', email='deposit@example.com', password='secret123')
        account = UserBankAccounts.objects.create(
            user=user,
            account_no=654321,
            account_type='Savings',
            gender='Male',
            balance=Decimal('0.00'),
        )

        client = Client()
        self.assertTrue(client.login(username='deposit-user', password='secret123'))

        response = client.post(
            reverse('deposite_money'),
            {'amount': '150.00', 'transaction_type': 1},
            follow=False,
        )

        account.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(account.balance, Decimal('150.00'))
