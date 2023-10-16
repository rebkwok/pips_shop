from salesman.admin.wagtail.panels import ReadOnlyPanel
from salesman.admin.wagtail.panels import OrderItemsPanel as SalesmanOrderItemsPanel
from salesman.admin.wagtail_hooks import OrderAdmin as SalesmanOrderAdmin
from salesman.core.utils import get_salesman_model
from wagtail.admin.ui.tables import BooleanColumn
from wagtail.contrib.modeladmin.options import modeladmin_register
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup

from .models import Product, CategoryPage, ProductVariant


Order = get_salesman_model("Order")


class ProductCategoryViewSet(SnippetViewSet):
    model = CategoryPage
    list_display = ("title", "index", BooleanColumn("live"), "get_product_count")
    list_editable = ("index", "live")


class ProductViewSet(SnippetViewSet):
    model = Product
    list_display = (
        "name",
        "category_link",
        "index",
        BooleanColumn("live"),
        "get_variant_count",
    )
    list_filter = ("category_page",)


class ProductVariantViewSet(SnippetViewSet):
    model = ProductVariant
    list_display = ("product", "variant_full_name", "category_link", "price", "stock", BooleanColumn("live"))
    list_filter = ("product",)


class ProductGroup(SnippetViewSetGroup):
    menu_label = "Shop Stock"
    menu_icon = "pick"
    items = (ProductCategoryViewSet, ProductViewSet, ProductVariantViewSet)


# class OrderItemsPanel(SalesmanOrderItemsPanel):
#     ...


class OrderAdmin(SalesmanOrderAdmin):
    SalesmanOrderAdmin.list_display.insert(2, "name")
    SalesmanOrderAdmin.list_display.insert(4, "shipping_method")
    SalesmanOrderAdmin.search_fields.append("name")
    SalesmanOrderAdmin.default_panels[2].children.insert(2, ReadOnlyPanel("name"))
    SalesmanOrderAdmin.default_panels[2].children.insert(3, ReadOnlyPanel("shipping_method"))
    # SalesmanOrderAdmin.default_items_panels = [
    #     OrderItemsPanel("items", heading="Items"),
    # ]


register_snippet(ProductGroup)
modeladmin_register(OrderAdmin)
