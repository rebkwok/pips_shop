# Generated by Django 4.2.6 on 2023-10-14 10:21

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("shop", "0016_basket_shipping_method"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="shipping_method",
            field=models.CharField(default=2, max_length=255),
            preserve_default=False,
        ),
    ]
