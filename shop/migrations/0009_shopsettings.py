# Generated by Django 4.2.4 on 2023-09-06 09:44

from django.db import migrations, models
import wagtail.contrib.forms.models


class Migration(migrations.Migration):
    dependencies = [
        ("shop", "0008_productvariant_image_alter_product_image_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="ShopSettings",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "notify_email_addresses",
                    models.CharField(
                        blank=True,
                        help_text="Optional - new orders will be emailed to these addresses. Separate multiple addresses by comma.",
                        max_length=255,
                        validators=[wagtail.contrib.forms.models.validate_to_address],
                    ),
                ),
                (
                    "reply_to",
                    models.EmailField(
                        blank=True,
                        help_text="Optional - reply to email address for shop notification emails.",
                        max_length=255,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
