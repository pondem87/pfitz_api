# Generated by Django 4.1.6 on 2023-04-13 09:25

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('zimgpt', '0004_profile_ref_alter_profile_wa_chat_state'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='ref',
            field=models.UUIDField(default=uuid.uuid4),
        ),
    ]