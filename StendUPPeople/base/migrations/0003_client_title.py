# Generated by Django 2.2.19 on 2024-06-20 00:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_follow'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='title',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]