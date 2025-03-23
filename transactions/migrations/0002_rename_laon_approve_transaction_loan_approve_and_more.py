# Generated by Django 5.1.1 on 2025-03-19 10:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='transaction',
            old_name='laon_approve',
            new_name='loan_approve',
        ),
        migrations.AlterField(
            model_name='transaction',
            name='transaction_type',
            field=models.IntegerField(choices=[(1, 'Deposite'), (2, 'Withdrawl'), (3, 'Loan'), (4, 'Loan Paid')], null=True),
        ),
    ]
