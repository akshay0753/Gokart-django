# Generated by Django 4.0.5 on 2025-03-11 11:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='address_1',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='order',
            name='address_2',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
