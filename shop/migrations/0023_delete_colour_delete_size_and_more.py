# Generated by Django 4.2.6 on 2023-10-15 18:28

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("shop", "0022_alter_productvariant_unique_together_and_more"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Colour",
        ),
        migrations.DeleteModel(
            name="Size",
        ),
        migrations.RenameField(
            model_name="productvariant",
            old_name="colour_name",
            new_name="colour",
        ),
        migrations.RenameField(
            model_name="productvariant",
            old_name="size_name",
            new_name="size",
        ),
        migrations.AlterUniqueTogether(
            name="productvariant",
            unique_together={("variant_name", "colour", "size")},
        ),
    ]