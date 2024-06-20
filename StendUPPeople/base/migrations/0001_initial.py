# Generated by Django 2.2.19 on 2024-06-19 18:53

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pub_date', models.DateTimeField(auto_now_add=True)),
                ('tg_id', models.IntegerField()),
                ('tg_username', models.CharField(blank=True, max_length=50, null=True)),
                ('joke', models.TextField()),
            ],
        ),
    ]
