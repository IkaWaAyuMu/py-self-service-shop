# Generated by Django 4.1.7 on 2023-03-24 05:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(max_length=200)),
                ('product_quanity', models.FloatField()),
                ('product_price', models.CharField(max_length=200)),
                ('product_serial_num', models.CharField(max_length=1000)),
            ],
        ),
    ]
