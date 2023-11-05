import pytest
import wagtail_factories

from model_bakery import baker
from salesman.core.utils import get_salesman_model


from ..models import CategoryPage, ShopPage


Basket = get_salesman_model("Basket")

Order = get_salesman_model("Order")

pytestmark = pytest.mark.django_db


class CategoryPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = CategoryPage


class ShopPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = ShopPage


@pytest.fixture
def shop_page(home_page):
    yield ShopPageFactory(parent=home_page)


@pytest.fixture
def category_page(shop_page):
    yield CategoryPageFactory(parent=shop_page, title="Test Category")


@pytest.fixture
def product(category_page):
    yield baker.make("shop.Product", name="Test Product", category_page=category_page)


@pytest.fixture
def basket(product):
    basket = baker.make("shop.Basket", extra={"name": "Test User"}, shipping_method="collect")
    variant = baker.make(
        "shop.ProductVariant", product=product, variant_name="Small", price=10,
        stock=5,
    )
    basket.add(variant, quantity=2)
    basket.update(request=None)
    yield basket


@pytest.fixture
def order(basket):
    yield Order.objects.create_from_basket(basket, request=None)
