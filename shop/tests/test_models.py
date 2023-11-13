from datetime import timedelta
import pytest
from model_bakery import baker

from django.test import RequestFactory
from django.utils import timezone
from django.urls import reverse

from salesman.core.utils import get_salesman_model

from .conftest import CategoryPageFactory


pytestmark = pytest.mark.django_db

Basket = get_salesman_model("Basket")


def test_category(category_page):
    assert category_page.get_product_count() == "0 live (0 total)"
    assert list(category_page.live_products) == []


def test_shop_page(shop_page, category_page):
    assert category_page.live
    # not live category
    CategoryPageFactory(parent=shop_page, title="Test Category 1", live=False)
    assert shop_page.children().count() == 1


def test_shop_page_context(shop_page):
    # needs to create basket from request
    request = RequestFactory().get("/")
    shop_context = shop_page.get_context(request)
    assert shop_context["basket_quantity"] == 0


def test_product(product):
    assert str(product) == "Test Product"
    assert product.get_variant_count() == "0 live (0 total)"
    assert list(product.live_variants) == []
    assert product.identifier == "test-category-test-product"
    assert product.get_absolute_url() == reverse("shop:product_detail", args=(product.id,))


def test_product_variant(product):
    variant = baker.make("shop.ProductVariant", product=product, variant_name="Small", price=10)
    assert str(variant) == "Test Product - Small"
    assert variant.get_price(None) == 10
    assert variant.category_link() == product.category_link()
    assert variant.code == str(variant.id)


@pytest.mark.parametrize(
    "variant_name,colour,size,expected_str,expected_name_and_price",
    [
        (None, None, None, "Test Product", "£10"),
        ("Mug", None, None, "Test Product - Mug", "Mug - £10"),
        (None, "Green", None, "Test Product - Green", "Green - £10"),
        ("T-shirt", None, "S", "Test Product - T-shirt - S", "T-shirt - S - £10"),
        ("T-shirt", "Black", None, "Test Product - T-shirt - Black", "T-shirt - Black - £10"),
        ("T-shirt", None, "One size", "Test Product - T-shirt - One size", "T-shirt - One size - £10"),
        ("T-shirt", "Red", "M", "Test Product - T-shirt - Red, M", "T-shirt - Red, M - £10"),
    ]
)
def test_product_variant_str(product, variant_name, colour, size, expected_str, expected_name_and_price):
    variant = baker.make(
        "shop.ProductVariant", 
        product=product, 
        variant_name=variant_name, 
        price=10
    )
    if colour:
        variant.colour = colour
        variant.save()
    if size:
        variant.size = size
        variant.save()
    
    assert str(variant) == variant.name == expected_str
    assert variant.name_and_price() == expected_name_and_price


def test_live_products(category_page, product):
    # product is live
    assert product.live
    # but has no variants yet
    assert not product.variants.exists()
    # so category live product count is still 0
    assert category_page.live_products.count() == 0

    # make a not-live variant
    variant = baker.make(
        "shop.ProductVariant", product=product, variant_name="Small", price=10, live=False
    )
    assert category_page.live_products.count() == 0
    assert product.variants.exists()
    assert product.live_variants.count() == 0

    # when the variant is live, the product is also properly live
    variant.live = True
    variant.save()
    assert product.live_variants.count() == 1
    assert category_page.live_products.count() == 1


def test_product_out_of_stock(product):
    # 2 variants, one out of stock
    variant = baker.make(
        "shop.ProductVariant", product=product, variant_name="Small", price=10, stock=5
    )
    baker.make(
        "shop.ProductVariant", product=product, variant_name="Medium", price=10, stock=0
    )

    assert not product.out_of_stock()

    variant.stock = 0
    variant.save()
    product.refresh_from_db()
    assert product.out_of_stock()


def test_product_out_of_stock_no_variants(product):
    assert not product.variants.exists()
    assert product.out_of_stock()


def test_product_images(product):
    # images are collated across product and product variants, duplicates are ignores
    image1 = baker.make("wagtailimages.Image")
    image2 = baker.make("wagtailimages.Image")
    product.image = image1
    product.save()
    baker.make(
        "shop.ProductVariant", product=product, variant_name="Small", price=10, image=image1
    )
    baker.make(
        "shop.ProductVariant", product=product, variant_name="Medium", price=10, image=image2
    )
    assert len(product.images) == 2


def test_basket_item(product):
    basket_item = baker.make("shop.BasketItem")
    assert basket_item.name == "(no name)"

    variant = baker.make(
        "shop.ProductVariant", product=product, variant_name="Small", price=10
    )
    basket_item.product = variant
    basket_item.quantity = 1
    basket_item.save()
    assert basket_item.name == "Test Product - Small"


def test_populate_order_from_basket(product):
    basket = baker.make("shop.Basket", extra={"name": "Test user"}, shipping_method="collect")
    variant = baker.make(
        "shop.ProductVariant", product=product, variant_name="Small", price=10
    )
    item = baker.make("shop.BasketItem", product=variant, quantity=2)
    basket.items.add(item)

    order = baker.make("shop.Order")
    order.populate_from_basket(basket=basket, request=None)
    assert order.items.count() == 1 
    assert order.shipping_method == "collect"
    assert order.name == "Test user"


def test_basket_timeout(basket, freezer):
    # initial timeout is in future
    assert basket.timeout > timezone.now()
    # clearing basked has no effect
    Basket.clear_expired()
    assert basket.items.exists()
    
    # move time to more than 15 mins in future
    freezer.move_to(timezone.now() + timedelta(minutes=20))
    Basket.clear_expired()
    assert not basket.items.exists()
