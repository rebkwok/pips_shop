# Generated by Django 4.2.6 on 2023-10-12 15:44

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields
import uuid
import wagtail.contrib.forms.models
import wagtail.fields
import wagtail.models


class Migration(migrations.Migration):
    dependencies = [
        ("wagtailcore", "0089_log_entry_data_json_null_to_object"),
        ("wagtailimages", "0025_alter_image_file_alter_rendition_file"),
        ("home", "0002_create_homepage"),
    ]

    operations = [
        migrations.AddField(
            model_name="homepage",
            name="body",
            field=wagtail.fields.RichTextField(
                default="", help_text="Main body text for the home page"
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="homepage",
            name="featured_section",
            field=models.ForeignKey(
                blank=True,
                help_text="First featured section for the homepage. Will display up to three child items.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="wagtailcore.page",
                verbose_name="Featured section 1",
            ),
        ),
        migrations.AddField(
            model_name="homepage",
            name="featured_section_body",
            field=wagtail.fields.RichTextField(
                blank=True,
                help_text="Optional description for the featured section",
                max_length=1000,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="homepage",
            name="featured_section_show_more_text",
            field=models.CharField(
                blank=True,
                help_text="Text to display for link to featured section",
                max_length=255,
            ),
        ),
        migrations.AddField(
            model_name="homepage",
            name="featured_section_title",
            field=models.CharField(
                blank=True,
                help_text="Title to display above the promo copy",
                max_length=255,
            ),
        ),
        migrations.AddField(
            model_name="homepage",
            name="hero_cta",
            field=models.CharField(
                default="",
                help_text="Text to display on Call to Action",
                max_length=255,
                verbose_name="Hero CTA",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="homepage",
            name="hero_cta_link",
            field=models.ForeignKey(
                blank=True,
                help_text="Choose a page to link to for the Call to Action",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="wagtailcore.page",
                verbose_name="Hero CTA link",
            ),
        ),
        migrations.AddField(
            model_name="homepage",
            name="hero_footer",
            field=models.CharField(
                blank=True,
                help_text="Text to display on the Footer link button",
                max_length=255,
                null=True,
                verbose_name="Hero Footer",
            ),
        ),
        migrations.AddField(
            model_name="homepage",
            name="hero_footer_link",
            field=models.ForeignKey(
                blank=True,
                help_text="Choose a page to link to for the Footer",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="wagtailcore.page",
                verbose_name="Hero CTA link",
            ),
        ),
        migrations.AddField(
            model_name="homepage",
            name="hero_footer_text",
            field=models.CharField(
                blank=True,
                help_text="Text to display on the home page footer image",
                max_length=255,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="homepage",
            name="hero_text",
            field=models.CharField(
                default="",
                help_text="Write a  short introduction for the home page",
                max_length=255,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="homepage",
            name="image",
            field=models.ForeignKey(
                blank=True,
                help_text="Homepage image",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="wagtailimages.image",
            ),
        ),
        migrations.AddField(
            model_name="homepage",
            name="page_link_1",
            field=models.ForeignKey(
                blank=True,
                help_text="First page link for the homepage.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="wagtailcore.page",
                verbose_name="Page link 1",
            ),
        ),
        migrations.AddField(
            model_name="homepage",
            name="page_link_1_btn_text",
            field=models.CharField(
                blank=True,
                help_text="Text to display on first page link button",
                max_length=255,
            ),
        ),
        migrations.AddField(
            model_name="homepage",
            name="page_link_1_image",
            field=models.ForeignKey(
                blank=True,
                help_text="Background image",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="wagtailimages.image",
            ),
        ),
        migrations.AddField(
            model_name="homepage",
            name="page_link_1_title",
            field=models.CharField(
                blank=True,
                help_text="Title to display for first page link",
                max_length=255,
            ),
        ),
        migrations.AddField(
            model_name="homepage",
            name="page_link_2",
            field=models.ForeignKey(
                blank=True,
                help_text="Second page link for the homepage.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="wagtailcore.page",
                verbose_name="Page link 2",
            ),
        ),
        migrations.AddField(
            model_name="homepage",
            name="page_link_2_btn_text",
            field=models.CharField(
                blank=True,
                help_text="Text to display on second page link button",
                max_length=255,
            ),
        ),
        migrations.AddField(
            model_name="homepage",
            name="page_link_2_image",
            field=models.ForeignKey(
                blank=True,
                help_text="Background image",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="wagtailimages.image",
            ),
        ),
        migrations.AddField(
            model_name="homepage",
            name="page_link_2_title",
            field=models.CharField(
                blank=True,
                help_text="Title to display for second page link",
                max_length=255,
            ),
        ),
        migrations.AddField(
            model_name="homepage",
            name="promo_image",
            field=models.ForeignKey(
                blank=True,
                help_text="Promo image",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="wagtailimages.image",
            ),
        ),
        migrations.AddField(
            model_name="homepage",
            name="promo_text",
            field=wagtail.fields.RichTextField(
                blank=True,
                help_text="Write some promotional copy",
                max_length=1000,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="homepage",
            name="promo_title",
            field=models.CharField(
                blank=True,
                help_text="Title to display above the promo copy",
                max_length=255,
            ),
        ),
        migrations.CreateModel(
            name="StandardPage",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.page",
                    ),
                ),
                (
                    "introduction",
                    models.TextField(blank=True, help_text="Text to describe the page"),
                ),
                (
                    "body",
                    wagtail.fields.RichTextField(blank=True, verbose_name="Page body"),
                ),
                (
                    "image",
                    models.ForeignKey(
                        blank=True,
                        help_text="Landscape mode only; horizontal width between 1000px and 3000px.",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="wagtailimages.image",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("wagtailcore.page",),
        ),
        migrations.CreateModel(
            name="FormPage",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.page",
                    ),
                ),
                (
                    "to_address",
                    models.CharField(
                        blank=True,
                        help_text="Optional - form submissions will be emailed to these addresses. Separate multiple addresses by comma.",
                        max_length=255,
                        validators=[wagtail.contrib.forms.models.validate_to_address],
                        verbose_name="to address",
                    ),
                ),
                (
                    "from_address",
                    models.EmailField(
                        blank=True, max_length=255, verbose_name="from address"
                    ),
                ),
                (
                    "subject",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="subject"
                    ),
                ),
                ("body", wagtail.fields.RichTextField(blank=True)),
                ("thank_you_text", wagtail.fields.RichTextField(blank=True)),
                (
                    "image",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="wagtailimages.image",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=(
                wagtail.contrib.forms.models.FormMixin,
                "wagtailcore.page",
                models.Model,
            ),
        ),
        migrations.CreateModel(
            name="FormField",
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
                    "sort_order",
                    models.IntegerField(blank=True, editable=False, null=True),
                ),
                (
                    "clean_name",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="Safe name of the form field, the label converted to ascii_snake_case",
                        max_length=255,
                        verbose_name="name",
                    ),
                ),
                (
                    "label",
                    models.CharField(
                        help_text="The label of the form field",
                        max_length=255,
                        verbose_name="label",
                    ),
                ),
                (
                    "field_type",
                    models.CharField(
                        choices=[
                            ("singleline", "Single line text"),
                            ("multiline", "Multi-line text"),
                            ("email", "Email"),
                            ("number", "Number"),
                            ("url", "URL"),
                            ("checkbox", "Checkbox"),
                            ("checkboxes", "Checkboxes"),
                            ("dropdown", "Drop down"),
                            ("multiselect", "Multiple select"),
                            ("radio", "Radio buttons"),
                            ("date", "Date"),
                            ("datetime", "Date/time"),
                            ("hidden", "Hidden field"),
                        ],
                        max_length=16,
                        verbose_name="field type",
                    ),
                ),
                (
                    "required",
                    models.BooleanField(default=True, verbose_name="required"),
                ),
                (
                    "choices",
                    models.TextField(
                        blank=True,
                        help_text="Comma or new line separated list of choices. Only applicable in checkboxes, radio and dropdown.",
                        verbose_name="choices",
                    ),
                ),
                (
                    "default_value",
                    models.TextField(
                        blank=True,
                        help_text="Default value. Comma or new line separated values supported for checkboxes.",
                        verbose_name="default value",
                    ),
                ),
                (
                    "help_text",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="help text"
                    ),
                ),
                (
                    "page",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="form_fields",
                        to="home.formpage",
                    ),
                ),
            ],
            options={
                "ordering": ["sort_order"],
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="FooterText",
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
                    "translation_key",
                    models.UUIDField(default=uuid.uuid4, editable=False),
                ),
                (
                    "live",
                    models.BooleanField(
                        default=True, editable=False, verbose_name="live"
                    ),
                ),
                (
                    "has_unpublished_changes",
                    models.BooleanField(
                        default=False,
                        editable=False,
                        verbose_name="has unpublished changes",
                    ),
                ),
                (
                    "first_published_at",
                    models.DateTimeField(
                        blank=True,
                        db_index=True,
                        null=True,
                        verbose_name="first published at",
                    ),
                ),
                (
                    "last_published_at",
                    models.DateTimeField(
                        editable=False, null=True, verbose_name="last published at"
                    ),
                ),
                (
                    "go_live_at",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="go live date/time"
                    ),
                ),
                (
                    "expire_at",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="expiry date/time"
                    ),
                ),
                (
                    "expired",
                    models.BooleanField(
                        default=False, editable=False, verbose_name="expired"
                    ),
                ),
                ("body", wagtail.fields.RichTextField()),
                (
                    "latest_revision",
                    models.ForeignKey(
                        blank=True,
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="wagtailcore.revision",
                        verbose_name="latest revision",
                    ),
                ),
                (
                    "live_revision",
                    models.ForeignKey(
                        blank=True,
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="wagtailcore.revision",
                        verbose_name="live revision",
                    ),
                ),
                (
                    "locale",
                    models.ForeignKey(
                        editable=False,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="wagtailcore.locale",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Footer Text",
                "abstract": False,
                "unique_together": {("translation_key", "locale")},
            },
            bases=(wagtail.models.PreviewableMixin, models.Model),
        ),
    ]
