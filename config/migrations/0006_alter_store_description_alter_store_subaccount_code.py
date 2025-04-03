# Generated by Django 5.1.7 on 2025-03-31 08:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0005_remove_deliverypartner_store_config_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='store',
            name='description',
            field=models.TextField(default=None, help_text='Description of the store', null=True),
        ),
        migrations.AlterField(
            model_name='store',
            name='subaccount_code',
            field=models.CharField(default=None, help_text='Subaccount code for transactions', max_length=100, null=True),
        ),
    ]
