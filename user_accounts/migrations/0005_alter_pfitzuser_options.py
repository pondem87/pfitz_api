# Generated by Django 4.1.6 on 2023-05-23 17:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_accounts', '0004_alter_pfitzuser_groups_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='pfitzuser',
            options={'verbose_name': 'user', 'verbose_name_plural': 'users'},
        ),
    ]