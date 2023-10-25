from decimal import Decimal
import pytest
from model_bakery import baker


pytestmark = pytest.mark.django_db


def test_basket_shipping_modifier(product):
    basket = baker.make("shop.Basket", extra={"name": "Test user"}, shipping_method="collect")
    variant = baker.make(
        "shop.ProductVariant", product=product, variant_name="Small", price=10
    )
    item = baker.make("shop.BasketItem", product=variant, quantity=2)
    basket.items.add(item)
    basket.update(request=None)
    assert basket.extra_rows == {}
    assert basket.subtotal == 20
    assert basket.total == 20

    basket.shipping_method = "deliver"
    basket.save()
    basket.update(request=None)

    assert list(basket.extra_rows.keys()) == ["shipping-cost"]
    assert basket.extra_rows["shipping-cost"].data == {'label': 'Shipping', 'amount': '3.99', 'extra': {}}
    assert basket.subtotal == 20
    assert pytest.approx(basket.total) == Decimal(23.99)
