# Generated by Django 4.2.6 on 2023-10-15 18:20

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("shop", "0019_product_price_productvariant_sort_order_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="productvariant",
            name="colour_name",
            field=models.CharField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="productvariant",
            name="size_name",
            field=models.CharField(blank=True, null=True),
        ),
    ]
