# Generated by Django 5.1.7 on 2025-03-28 23:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Store',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('business_name', models.CharField(help_text='Name of the business managing the store', max_length=100)),
                ('settlement_bank', models.CharField(help_text='Bank code for settlement', max_length=10)),
                ('account_number', models.CharField(help_text='Bank account number for settlements', max_length=15)),
                ('percentage_charge', models.DecimalField(decimal_places=2, help_text='Percentage charge applied to transactions', max_digits=5)),
            ],
        ),
    ]
