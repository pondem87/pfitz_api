# Generated by Django 4.1.6 on 2023-03-02 21:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0006_alter_payment_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='mobile_wallet_number',
            field=models.CharField(max_length=20, null=True),
        ),
    ]