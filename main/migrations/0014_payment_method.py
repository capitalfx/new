# Generated by Django 3.2.8 on 2021-11-18 23:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_remove_replys_to'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment_Method',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100)),
                ('Message', models.CharField(blank=True, max_length=1000)),
            ],
        ),
    ]
