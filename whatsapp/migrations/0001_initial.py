# Generated by Django 4.1.6 on 2023-03-01 18:22

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ReceivedMessages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wamid', models.CharField(max_length=256, null=True)),
                ('user_number', models.CharField(max_length=15)),
                ('user_wa_id', models.CharField(max_length=128)),
                ('message_type', models.CharField(max_length=128)),
                ('message_text', models.TextField(default=None, null=True)),
                ('read', models.BooleanField(default=False)),
                ('read_notified', models.BooleanField(default=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='SentMessages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wamid', models.CharField(max_length=256, null=True)),
                ('user_number', models.CharField(max_length=15)),
                ('user_wa_id', models.CharField(max_length=128)),
                ('message_type', models.CharField(max_length=128)),
                ('message_text', models.TextField(default=None, null=True)),
                ('template_name', models.CharField(default=None, max_length=128, null=True)),
                ('status', models.CharField(max_length=50, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
