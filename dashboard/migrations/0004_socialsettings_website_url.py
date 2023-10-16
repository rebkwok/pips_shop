# Generated by Django 4.2.6 on 2023-10-16 14:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("dashboard", "0003_alter_sitesettings_title_suffix"),
    ]

    operations = [
        migrations.AddField(
            model_name="socialsettings",
            name="website_url",
            field=models.URLField(blank=True, verbose_name="Website URL"),
        ),
    ]
