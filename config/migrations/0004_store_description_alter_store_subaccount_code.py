# Generated by Django 5.1.7 on 2025-03-30 18:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0003_store_subaccount_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='store',
            name='description',
            field=models.TextField(default=None, help_text='Description of the store'),
        ),
        migrations.AlterField(
            model_name='store',
            name='subaccount_code',
            field=models.CharField(default=None, help_text='Subaccount code for transactions', max_length=100),
        ),
    ]
