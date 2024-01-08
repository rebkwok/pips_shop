# Generated by Django 4.2.6 on 2024-01-08 09:04

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):
    dependencies = [
        ("shop", "0028_sale_banner_content_sale_banner_include_end_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sale",
            name="banner_include_end",
            field=models.BooleanField(
                default=False,
                help_text="Include end date in banner (displayed as 'Sale ends on dd mmm yyyy at HH:MM')",
                verbose_name="Include end date in banner",
            ),
        ),
        migrations.AlterField(
            model_name="salecategory",
            name="sale",
            field=modelcluster.fields.ParentalKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="sale_categories",
                to="shop.sale",
            ),
        ),
        migrations.AlterField(
            model_name="saleproduct",
            name="sale",
            field=modelcluster.fields.ParentalKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="sale_products",
                to="shop.sale",
            ),
        ),
    ]