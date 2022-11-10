# Generated by Django 3.2.8 on 2021-11-23 14:40

from decimal import Decimal
from django.db import migrations
import djmoney.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0019_auto_20211123_1537'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usertype',
            name='balance',
            field=djmoney.models.fields.MoneyField(decimal_places=1, default=Decimal('0'), default_currency='USD', max_digits=14),
        ),
        migrations.AlterField(
            model_name='usertype',
            name='invested_balance',
            field=djmoney.models.fields.MoneyField(decimal_places=1, default=Decimal('0'), default_currency='USD', max_digits=14),
        ),
    ]
