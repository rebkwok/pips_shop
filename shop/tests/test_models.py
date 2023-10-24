import pytest
from model_bakery import baker
import wagtail_factories

from ..models import CategoryPage, ShopPage

pytestmark = pytest.mark.django_db


class CategoryPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = CategoryPage


class ShopPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = ShopPage


@pytest.fixture
def shop_page(root_page):
    yield ShopPageFactory(parent=root_page)


@pytest.fixture
def category_page(shop_page):
    yield CategoryPageFactory(parent=shop_page, title="Test Category")


@pytest.fixture
def product(category_page):
    yield baker.make("shop.Product", name="Test Product", category_page=category_page)


def test_category(category_page):
    assert category_page.get_product_count() == "0 live (0 total)"
    assert list(category_page.live_products) == []


def test_product(product):
    assert str(product) == "Test Product"
    assert product.get_variant_count() == "0 live (0 total)"
    assert list(product.live_variants) == []
    assert product.identifier == "test-category-test-product"


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
    
    assert str(variant) == expected_str
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
