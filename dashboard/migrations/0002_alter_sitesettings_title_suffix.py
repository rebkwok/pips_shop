# Generated by Django 4.2.6 on 2023-10-12 15:47

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("dashboard", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sitesettings",
            name="title_suffix",
            field=models.CharField(
                default="Podencos In Need (PINS)",
                help_text="The suffix for the title meta tag e.g. ' | Podencos In Need (PINS)'",
                max_length=255,
                verbose_name="Title suffix",
            ),
        ),
    ]
