# Generated by Django 4.2.6 on 2023-10-14 10:22

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("shop", "0017_order_shipping_method"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="shipping_method",
            field=models.CharField(
                choices=[("collect", "Collect in store"), ("deliver", "delivery")],
                default="collect",
            ),
        ),
    ]
