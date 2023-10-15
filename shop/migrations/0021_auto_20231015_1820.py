# Generated by Django 4.2.6 on 2023-10-15 18:20

from django.db import migrations


def colour_and_size_forwards(apps, schema_editor):
    ProductVariant = apps.get_model("shop", "ProductVariant")
    for variant in ProductVariant.objects.all():
        if variant.colour:
            variant.colour_name = variant.colour.name
        if variant.size:
            variant.size_name = variant.size.name
        variant.save()


class Migration(migrations.Migration):
    dependencies = [
        ("shop", "0020_productvariant_colour_name_productvariant_size_name"),
    ]

    operations = [
        migrations.RunPython(colour_and_size_forwards, migrations.RunPython.noop),
    ]
