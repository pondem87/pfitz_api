# Generated by Django 4.1.6 on 2023-03-02 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='discontinued_on',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
