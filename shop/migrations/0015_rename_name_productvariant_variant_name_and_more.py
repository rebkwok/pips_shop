# Generated by Django 4.2.6 on 2023-10-13 14:37

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("shop", "0014_alter_productvariant_colour_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="productvariant",
            old_name="name",
            new_name="variant_name",
        ),
        migrations.AlterUniqueTogether(
            name="productvariant",
            unique_together={("variant_name", "colour", "size")},
        ),
    ]
