import logging
from django.db import models, transaction
from django.http import HttpRequest
from django.urls import reverse
from django.utils.text import slugify
from django.utils.safestring import mark_safe
from salesman.basket.models import BaseBasket, BaseBasketItem
from salesman.orders.models import (
    BaseOrder,
    BaseOrderItem,
    BaseOrderNote,
    BaseOrderPayment,
)
from modelcluster.models import ClusterableModel, ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel, HelpPanel
from wagtail.contrib.forms.models import validate_to_address
from wagtail.contrib.settings.models import (
    BaseGenericSetting,
    register_setting,
)
from wagtail.fields import RichTextField
from wagtail.models import Page, Orderable


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
        # Note product here is a ProductVariant instance
        return self.product.name if self.product else "(no name)"


# PRODUCTS


class CategoryPage(Page):
    body = RichTextField(
        verbose_name="Page body",
        blank=True,
        help_text="Optional text to describe the category",
    )
    index = models.PositiveIntegerField(
        default=100, help_text="Used for ordering categories on the shop page"
    )

    content_panels = Page.content_panels + [
        FieldPanel("body"),
        FieldPanel("index"),
    ]

    parent_page_types = ["ShopPage"]
    subpage_types = ["CategoryPage"]

    def get_product_count(self):
        return f"{self.live_products.count()} live ({self.page_products.count()} total)"
    get_product_count.short_description = "# products"

    @property
    def live_products(self):
        # products are live if they are set to live AND have at least one live variant
        return (
            self.page_products.filter(live=True, variants__isnull=False, variants__live=True)
            .order_by("index")
            .distinct()
        )
 

class Product(ClusterableModel):
    """
    Product, used to subgroup products in display.
    ProductVariant is the actual product that gets added to basket.
    """
    category_page = ParentalKey(CategoryPage, related_name="page_products")

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
    price = models.DecimalField(
        max_digits=18, decimal_places=2, default=10, 
        help_text="Default price for this product. Can be overridden by setting price on individual variants."
    ) 
    index = models.PositiveIntegerField(
        default=100, help_text="Used for ordering products on the category page"
    )
    live = models.BooleanField(
        default=True, help_text="Display this product in the shop"
    )

    panels = [
        HelpPanel(
            """
            A Product is an item for sale; it has a name and a description.
            
            Product variants represent the actual items that are sold, and may have attributes e.g. size
            and colour. Each product must have at least one variant in order to be available for sale.
            """
        ),
        FieldPanel('category_page'),
        FieldPanel('name'),
        FieldPanel('image'),
        FieldPanel("price"),
        FieldPanel('description'),
        FieldPanel('index'),
        FieldPanel('live'),
        InlinePanel(
            "variants", heading="Product variants", label="Variant", 
            help_text=mark_safe("""A variant represents a single item that can be ordered/purchased. E.g.
            A product 'Pen' might have variants 'Single', 'Pack of 5', 'Pack of 10'.<br/>
            Can be left blank if there is only one variant for this product, or if it
            only varies by colour and/or size.<br/> 
            e.g.
            <ul>
            <li>Product Mug: one product variant, with no name, colour or size specifications.</li>
            <li>Product T-shirt: size/colour variants with no separate name (e.g. black,S)</li>
            <li>Product Hoodie: variants with name "Men's Hoodie", "Women's Hoodie", each 
              with size and colour options</li>
            </ul>
            Use the arrows to reorder items.
            """)
        ),
    ]

    def __str__(self):
        return self.name

    def get_variant_count(self):
        return f"{self.live_variants.count()} live ({self.variants.count()} total)"

    get_variant_count.short_description = "# variants"

    @property
    def live_variants(self):
        return self.variants.filter(live=True)

    def out_of_stock(self):
        if self.variants.exists():
            return self.variants.aggregate(models.Sum("stock"))["stock__sum"] <= 0
        return True

    @property
    def identifier(self):
        return slugify(f"{self.category_page.title}-{self.name}")

    def category_link(self):
        return mark_safe(
            f"<a href={reverse('wagtailadmin_pages:edit', args=(self.category_page.id,))}>{self.category_page.title}</a>"
        )
    category_link.short_description = "Category"

    @property
    def images(self):
        all_images = list()
        if self.image:
            all_images.append(self.image)
        for variant in self.live_variants.filter(image__isnull=False):
            if variant.image not in all_images:
                all_images.append(variant.image)
        return all_images


class ProductVariant(Orderable):
    product = ParentalKey(
        Product, on_delete=models.CASCADE, related_name="variants"
    )
    variant_name = models.CharField(
        null=True, blank=True,
        max_length=255,
        verbose_name="Variant name",
        help_text="Can be left blank if there is only one variant for this product.",
    )
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    price = models.DecimalField(
        null=True, blank=True, max_digits=18, decimal_places=2,
        help_text="Leave blank to use default product price."
    )
    stock = models.IntegerField(default=1, help_text="Quantity of this item currently in stock")
    live = models.BooleanField(
        default=True, help_text="Display this product variant in the shop"
    )

    colour = models.CharField(null=True, blank=True)
    size = models.CharField(null=True, blank=True)

    class Meta:
        unique_together = ("variant_name", "colour", "size")

    def __str__(self):
        product_name = self.product.name
        if self.variant_full_name():
            return f"{product_name} - {self.variant_full_name()}"
        return product_name

    @property
    def name(self):
        return str(self)

    def variant_full_name(self):
        name = self.variant_name or ""
        if name and (self.colour or self.size):
            name += " - "
        if self.colour:
            name += self.colour
            if self.size:
                name += ", "
        if self.size:
            name += self.size
        return name
    variant_full_name.short_description = "Variant name"

    def get_price(self, request):
        return self.price

    def name_and_price(self):
        if self.variant_full_name():
            return f"{self.variant_full_name()} - £{self.price}"
        return f"£{self.price}"

    def category_link(self):
        return mark_safe(
            f"<a href={reverse('wagtailadmin_pages:edit', args=(self.product.category_page.id,))}>{self.product.category_page.title}</a>"
        )
    category_link.short_description = "Category"
    category_link.admin_order_field = "product__category_page__title"
    category_link.short_description = "Category"
    
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
    subpage_types = ["home.FormPage", "home.StandardPage", "CategoryPage"]

    def categories(self):
        return CategoryPage.objects.live().order_by("index")

    def children(self):
        return self.categories()

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
