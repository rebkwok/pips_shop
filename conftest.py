
from datetime import datetime
from datetime import timezone as datetime_tz
import pytest

from wagtail.models import Site

import wagtail_factories

from model_bakery import baker
from salesman.core.utils import get_salesman_model

from shop.models import SaleCategory, SaleProduct
from shop.tests.factories import CategoryPageFactory, ShopPageFactory

Basket = get_salesman_model("Basket")

Order = get_salesman_model("Order")

pytestmark = pytest.mark.django_db

class HomePageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = "home.HomePage"


@pytest.fixture
def home_page(autouse=True):
    root_page = wagtail_factories.PageFactory(parent=None)
    page = HomePageFactory(
        parent=root_page,
        title="Home",
        hero_text="Home",
        hero_cta="Test",
        body="Test",
    )
    Site.objects.create(
        hostname="localhost",
        port=8000,
        root_page=page,
        is_default_site=True,
    )
    yield page


@pytest.fixture
def shop_page(home_page):
    yield ShopPageFactory(parent=home_page)


@pytest.fixture
def category_page(shop_page):
    yield CategoryPageFactory(parent=shop_page, title="Test Category")


@pytest.fixture
def product(category_page):
    yield baker.make(
        "shop.Product", name="Test Product", category_page=category_page, price=12
    )


@pytest.fixture
def basket(product):
    basket = baker.make(
        "shop.Basket", extra={"name": "Test User"}, shipping_method="collect"
    )
    variant = baker.make(
        "shop.ProductVariant",
        product=product,
        variant_name="Small",
        price=10,
        stock=5,
    )
    basket.add(variant, quantity=2)
    basket.update(request=None)
    yield basket


@pytest.fixture
def order(basket):
    yield Order.objects.create_from_basket(basket, request=None)


@pytest.fixture
def sale_with_items(product):
    sale = baker.make(
        "shop.Sale",
        name="Test Sale",
        start_date=datetime(2022, 1, 1, tzinfo=datetime_tz.utc),
        end_date=datetime(2022, 1, 2, tzinfo=datetime_tz.utc),
    )
    SaleCategory.objects.create(category=product.category_page, discount=10, sale=sale)
    SaleProduct.objects.create(product=product, discount=20, sale=sale)
    yield sale
