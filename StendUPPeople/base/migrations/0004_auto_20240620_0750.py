# Generated by Django 2.2.19 on 2024-06-20 00:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_client_title'),
    ]

    operations = [
        migrations.RenameField(
            model_name='client',
            old_name='title',
            new_name='subject',
        ),
    ]