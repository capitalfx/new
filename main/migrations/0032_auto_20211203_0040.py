# Generated by Django 3.2.8 on 2021-12-02 23:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0031_withdrawmodel'),
    ]

    operations = [
        migrations.AddField(
            model_name='investmentmodel',
            name='crypto_amount',
            field=models.CharField(blank=True, default='0.008', max_length=100),
        ),
        migrations.AddField(
            model_name='investmentmodel',
            name='payMethod',
            field=models.CharField(blank=True, default='Bitcoin', max_length=100),
        ),
    ]
