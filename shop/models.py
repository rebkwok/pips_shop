import logging
from django.db import models, transaction
from django.http import HttpRequest
from django.urls import reverse
from django.utils.text import slugify
from salesman.basket.models import BaseBasket, BaseBasketItem
from salesman.orders.models import (
    BaseOrder,
    BaseOrderItem,
    BaseOrderNote,
    BaseOrderPayment,
)
from wagtail.admin.panels import FieldPanel
from wagtail.contrib.forms.models import validate_to_address
from wagtail.contrib.settings.models import (
    BaseGenericSetting,
    register_setting,
)
from wagtail.fields import RichTextField
from wagtail.models import Page


# ORDERS


SHIPPING_METHODS = {
    "collect": "Collect in store", 
    "deliver": "Delivery"
}

logger = logging.getLogger(__name__)


class Order(BaseOrder):
    name = models.CharField(max_length=255, verbose_name="Name")
    shipping_method = models.CharField(
        choices=tuple(SHIPPING_METHODS.items()),
        default="collect"
    )

    @transaction.atomic
    def populate_from_basket(
        self,
        basket,
        request,
        **kwargs,
    ) -> None:
        basket.extra["basket_id"] = basket.id
        self.name = basket.extra.pop("name", "")
        self.shipping_method = basket.shipping_method
        return super().populate_from_basket(basket, request, **kwargs)


class OrderItem(BaseOrderItem):
    pass


class OrderPayment(BaseOrderPayment):
    pass


class OrderNote(BaseOrderNote):
    pass


# BASKET


class Basket(BaseBasket):
    shipping_method = models.CharField(
        choices=tuple(SHIPPING_METHODS.items()),
        default="collect"
    )


class BasketItem(BaseBasketItem):
    
    @property
    def name(self):
        return self.product.get_full_name() if self.product else "(no name)"


# PRODUCTS


class ProductCategory(models.Model):
    """
    Product category, used to categorise products in display.
    ProductVariant is the actual product that gets added to basket.
    e.g.
    Category = Clothing
    ProductType = T-shirt
    ProductVariant = Mens Medium
    or
    e.g.
    Category = Merchandise
    ProductType = Pen
    ProductVariant = Pack of 10
    """

    name = models.CharField(max_length=255)
    body = RichTextField(
        verbose_name="Page body",
        blank=True,
        help_text="Optional text to describe the category",
    )
    index = models.PositiveIntegerField(
        default=100, help_text="Used for ordering categories on the shop page"
    )
    live = models.BooleanField(
        default=True, help_text="Display this category in the shop"
    )

    class Meta:
        verbose_name_plural = "product categories"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("shop:productcategory_detail", kwargs={"pk": self.pk})

    def get_product_count(self):
        return f"{self.live_products.count()} live ({self.products.count()} total)"

    get_product_count.short_description = "# products"

    @property
    def live_products(self):
        # products are live if they are set to live AND have at least one live variant
        return (
            self.products.filter(live=True, variants__isnull=False, variants__live=True)
            .order_by("index")
            .distinct()
        )


class Product(models.Model):
    """
    Product, used to subgroup products in display.
    ProductVariant is the actual product that gets added to basket.
    """

    category = models.ForeignKey(
        ProductCategory, on_delete=models.CASCADE, related_name="products"
    )
    name = models.CharField(max_length=255)

    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Images can be added to product and/or product variants, all will be displayed",
    )
    description = RichTextField(help_text="Description of the product", blank=True)
    index = models.PositiveIntegerField(
        default=100, help_text="Used for ordering products on the category page"
    )
    live = models.BooleanField(
        default=True, help_text="Display this product in the shop"
    )

    def __str__(self):
        return self.name

    def get_variant_count(self):
        return f"{self.live_variants.count()} live ({self.variants.count()} total)"

    get_variant_count.short_description = "# variants"

    @property
    def live_variants(self):
        return self.variants.filter(live=True)

    def out_of_stock(self):
        return self.variants.aggregate(models.Sum("stock"))["stock__sum"] <= 0

    @property
    def identifier(self):
        return slugify(f"{self.category.name}-{self.name}")

    @property
    def images(self):
        all_images = []
        if self.image:
            all_images.append(self.image)
        for variant in self.live_variants.filter(image__isnull=False):
            all_images.append(variant.image)
        return all_images


class Size(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name
    

class Colour(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class ProductVariant(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="variants"
    )
    variant_name = models.CharField(
        null=True, blank=True,
        max_length=255,
        verbose_name="Variant name",
        help_text="""
            A variant represents a single item that can be ordered/purchased. E.g.
            A product 'Pen' might have variants 'Single', 'Pack of 5', 'Pack of 10'.
            Can be left blank if there is only one variant for this product, or if it
            only varies by colour and/or size. 
            e.g. 
            - Product Mug: one product variant, with no name, colour or size specifications.
            - Product T-shirt: size/colour variants with no separate name (e.g. black,S)
            - Product Hoodie: variants with name "Men's Hoodie", "Women's Hoodie", each 
              with size and colour options
        """,
    )
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    price = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    stock = models.IntegerField(default=1, help_text="Quantity of this item currently in stock")
    live = models.BooleanField(
        default=True, help_text="Display this product variant in the shop"
    )

    colour = models.ForeignKey(Colour, null=True, blank=True, on_delete=models.SET_NULL)
    size = models.ForeignKey(Size, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        unique_together = ("variant_name", "colour", "size")

    def __str__(self):
        product_name = self.product.name
        if self.name:
            return f"{product_name} - {self.name}"
        return product_name

    def get_full_name(self):
        return str(self)

    @property
    def name(self):
        name = self.variant_name or ""
        if name and (self.colour or self.size):
            name += " - "
        if self.colour:
            name += str(self.colour)
            if self.size:
                name += ", "
        if self.size:
            name += str(self.size)
        return name

    def get_price(self, request):
        return self.price

    def name_and_price(self):
        if self.name:
            return f"{self.name} - £{self.price}"
        return f"£{self.price}"

    @property
    def category(self):
        return self.product.category

    def get_category(self):
        return self.category

    get_category.admin_order_field = "product__category"
    get_category.short_description = "Category"

    @property
    def code(self):
        return str(self.id)


class ShopPage(Page):
    introduction = models.TextField(help_text="Text to describe the page", blank=True)
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Landscape mode only; horizontal width between 1000px and 3000px.",
    )
    body = RichTextField(verbose_name="Page body", blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("introduction"),
        FieldPanel("body"),
        FieldPanel("image"),
    ]

    parent_page_types = ["home.HomePage"]

    def categories(self):
        return ProductCategory.objects.filter(live=True).order_by("index")

    def get_context(self, request):
        from .views import get_basket_quantity

        context = super().get_context(request)
        context["basket_quantity"] = get_basket_quantity(request)
        return context


@register_setting
class ShopSettings(BaseGenericSetting):
    notify_email_addresses = models.CharField(
        max_length=255,
        blank=True,
        help_text=(
            "Optional - new orders will be emailed to these addresses. "
            "Separate multiple addresses by comma."
        ),
        validators=[validate_to_address],
    )
    reply_to = models.EmailField(
        max_length=255,
        blank=True,
        help_text=("Optional - reply to email address for shop notification emails."),
    )

    panels = [
        FieldPanel("notify_email_addresses"),
        FieldPanel("reply_to"),
    ]
