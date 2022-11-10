# Generated by Django 3.2.8 on 2021-12-05 15:32

from decimal import Decimal
from django.db import migrations
import djmoney.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0033_auto_20211204_1354'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usertype',
            name='bonus',
            field=djmoney.models.fields.MoneyField(decimal_places=1, default=Decimal('0'), default_currency='USD', max_digits=14),
        ),
        migrations.AlterField(
            model_name='usertype',
            name='commision',
            field=djmoney.models.fields.MoneyField(decimal_places=1, default=Decimal('0'), default_currency='USD', max_digits=14),
        ),
    ]
