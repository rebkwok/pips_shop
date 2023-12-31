# Generated by Django 4.2.6 on 2023-10-15 18:27

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("shop", "0021_auto_20231015_1820"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="productvariant",
            unique_together={("variant_name", "colour_name", "size_name")},
        ),
        migrations.RemoveField(
            model_name="productvariant",
            name="colour",
        ),
        migrations.RemoveField(
            model_name="productvariant",
            name="size",
        ),
    ]
