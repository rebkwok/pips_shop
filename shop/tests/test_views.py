from unittest import mock

import pytest

from model_bakery import baker

from django.urls import reverse

from salesman.core.utils import get_salesman_model

from ..views import (
    add_to_basket,
    basket_view,
    decrease_quantity, 
    get_basket, 
    get_basket_item,
    get_basket_total,
    get_basket_quantity_and_total,
    _can_increase_quantity, 
    increase_quantity,
    update_quantity,
    delete_basket_item,
    checkout_view,
    new_order_view,
    order_status_view,
)


Basket = get_salesman_model("Basket")

pytestmark = pytest.mark.django_db


def test_get_basket(rf):
    request = rf.get('/')
    assert not Basket.objects.exists()
    basket_resp = get_basket(request)
    assert Basket.objects.count() == 1
    assert basket_resp == {
        'extra': {},
        'extra_rows': [],
        'id': Basket.objects.first().id,
        'items': [],
        'subtotal': '0.00',
        'total': '0.00'
    }


def test_get_basket_total(rf):
    request = rf.get('/')
    basket_resp = get_basket_total(request)
    assert basket_resp == "0.00"


def test_get_basket_quantity_and_total(rf):
    request = rf.get('/')
    basket_resp = get_basket_quantity_and_total(request)
    assert basket_resp == (0, "0.00")


def test_get_existing_empty_basket(rf):
    basket = baker.make(Basket)
    request = rf.get('/')
    request.session = {"BASKET_ID": basket.id}
    
    assert get_basket(request) == {
        'extra': {},
        'extra_rows': [],
        'id': basket.id,
        'items': [],
        'subtotal': '0.00',
        'total': '0.00'
    }


def test_get_basket_with_items(rf, basket):
    request = rf.get('/')
    request.session = {"BASKET_ID": basket.id}
    basket_resp = get_basket(request)
    basket_items = basket_resp.pop("items")
    assert basket_resp == {
        'extra': {'name': 'Test User'},
        'extra_rows': [],
        'id': basket.id,
        'subtotal': '20.00',
        'total': '20.00'
    }
    assert len(basket_items) == 1
    basket_item = basket_items[0]
    assert basket_item["quantity"] == 2
    assert basket_item["product"]["name"] == 'Test Product - Small'


def test_get_basket_item(rf, basket, product):
    request = rf.get('/')
    # no basket
    basket_resp = get_basket(request)
    get_basket_item(basket_resp, product.id) == {}
    # with basket
    request.session = {"BASKET_ID": basket.id}
    basket_resp = get_basket(request)
    basket_item = get_basket_item(basket_resp, product.id)
    assert basket_item["product"]["name"] == 'Test Product - Small'


def test_get_product_detail_view(client, product):
    resp = client.get(reverse("shop:product_detail", args=(product.id,)))
    assert resp.status_code == 200


@pytest.mark.parametrize(
    "current_stock,increase_to,in_basket,expected",
    [
        # changing quantity to 1
        # out of stock
        (0, 1, False, False),
        # But if we're in the basket, it's actually a decrease (basket quantity is 2)
        (0, 1, True, True),
        # stock 1; can increase to 1 from in and out of basket
        (1, 1, False, True),
        (1, 1, True, True),
        # can increase basket quantity to 3 (currently 2) from in basket but not outside
        (1, 3, True, True),
        (1, 3, False, False)
    ]
)
def test_can_increase_quantity(rf, basket, product, current_stock, increase_to, in_basket, expected):
    # 2 items in basket already
    variant = product.variants.first()
    variant.stock = current_stock
    variant.save()

    request = rf.get('/')
    request.session = {"BASKET_ID": basket.id}

    assert _can_increase_quantity(request, variant, increase_to, in_basket) == expected

    
def test_increase_quantity_can_increase(rf, basket, product):
    # 2 items in basket already, ensure we can increase
    variant = product.variants.first()
    variant.stock = 2
    variant.save()
    # salesman requires that the parameter name when submitting a product to the 
    # basket is "product_id"; a basket product is actually a product variant
    url = reverse("shop:increase_quantity", args=(product.id,)) + f"?product_id={variant.id}&quantity=1" 
    request = rf.get(url)
    request.session = {"BASKET_ID": basket.id}

    response = increase_quantity(request, product.id)
    assert response.headers['HX-Trigger'] == "quantity-changed"
    assert "value=2" in response.content.decode()


def test_increase_quantity_cannot_increase(rf, basket, product):
    # 2 items in basket already, can't increase
    variant = product.variants.first()
    variant.stock = 0
    variant.save()
    # salesman requires that the parameter name when submitting a product to the 
    # basket is "product_id"; a basket product is actually a product variant
    url = reverse("shop:increase_quantity", args=(product.id,)) + f"?product_id={variant.id}&quantity=2" 
    request = rf.get(url)
    request.session = {"BASKET_ID": basket.id}

    response = increase_quantity(request, product.id)
    assert 'HX-Trigger' not in response.headers
    assert "value=2" in response.content.decode()


def test_increase_quantity_from_basket(rf, basket, product):
    # 2 items in basket already, ensure we can increase
    variant = product.variants.first()
    variant.stock = 0
    variant.save()
    # salesman requires that the parameter name when submitting a product to the 
    # basket is "product_id"; a basket product is actually a product variant
    url = reverse("shop:increase_quantity", args=(product.id,)) + f"?product_id={variant.id}&quantity=1&ref=basket" 
    request = rf.get(url)
    request.session = {"BASKET_ID": basket.id}

    response = increase_quantity(request, product.id)
    assert response.headers['HX-Trigger'] == "quantity-changed"
    assert "value=2" in response.content.decode()


@pytest.mark.parametrize(
    "current_quantity,expected",
    [
        (1, 1),
        (2, 1),
        (3, 2)
    ]
)
def test_decrease_quantity(rf, basket, product, current_quantity, expected):
    variant = product.variants.first()
    variant.stock = 0
    variant.save()
    # salesman requires that the parameter name when submitting a product to the 
    # basket is "product_id"; a basket product is actually a product variant
    url = reverse("shop:decrease_quantity", args=(product.id,)) + f"?product_id={variant.id}&quantity={current_quantity}" 
    request = rf.get(url)
    request.session = {"BASKET_ID": basket.id}

    response = decrease_quantity(request, product.id)
    assert response.headers['HX-Trigger'] == "quantity-changed"
    assert f"value={expected}" in response.content.decode()


def test_basket_view(rf, basket, product):
    request = rf.get(reverse("shop:basket"))
    request.session = {"BASKET_ID": basket.id}
    resp = basket_view(request)
    assert resp.context_data["payment_methods"] == [
        {"identifier": "stripe", "label": "Pay with Stripe", "error": None, "help": "Pay with stripe"}
    ]
    assert resp.context_data["shipping_methods"] == [
        ("collect", "Collect in store"), ("deliver", "Delivery")
    ]
    # basket items are converted to a dict keyed by product, with product type and category added
    assert list(resp.context_data["basket"]["items"].keys()) == [product.identifier]
    item = resp.context_data["basket"]["items"][product.identifier][0]
    assert item["product_type"] == product.name
    assert item["category"] == product.category_page.title


def test_add_to_basket(rf, product):
    # setup empty basket
    request = rf.get('/')
    basket_id = get_basket(request)["id"]
    variant = baker.make(
        "shop.ProductVariant", product=product, variant_name="Small", price=10,
        stock=4
    )
    request = rf.post(
        reverse("shop:add_to_basket", args=(product.id,)),
        {"quantity": 3, "product_id": variant.id, "product_type": "shop.ProductVariant"}
    )
    request.session = {"BASKET_ID": basket_id}
    resp = add_to_basket(request, product.id)
    content = resp.content.decode()
    # 3 items in basket
    assert '<i class="fa-solid fa-basket-shopping"></i>  (3)' in content
    # quantity reset to 1
    assert f'id="id_quantity_{product.id}" name="quantity" type="number" value=1' in content
    assert f'<option value="{variant.id}">Small - £10.00 (1 in stock)</option>'


def test_add_to_basket_out_of_stock(rf, basket, product):
    # setup empty basket
    variant1 = product.variants.first()
    variant1.stock = 2
    variant1.save()
    variant2 = baker.make(
        "shop.ProductVariant", product=product, variant_name="Medium", price=10,
        stock=2
    )
    # add to basket so variant1 becomes out of stock
    request = rf.post(
        reverse("shop:add_to_basket", args=(product.id,)),
        {"quantity": 2, "product_id": variant1.id, "product_type": "shop.ProductVariant"}
    )
    request.session = {"BASKET_ID": basket.id}
    resp = add_to_basket(request, product.id)
    content = resp.content.decode()
    # 4 item now in basket
    assert '<i class="fa-solid fa-basket-shopping"></i>  (4)' in content
    
    # variant 1 out of stock; another variant still in stock, so quantity and +/- buttons still shown
    assert f'id="id_quantity_{product.id}" name="quantity" type="number" value=1' in content
    assert f'<option disabled=disabled value="{variant1.id}">Small - £10.00 (out of stock)</option>' in content
    assert f'<option value="{variant2.id}">Medium - £10.00 (2 in stock)</option>'

    # add to basket so variant2 now also out of stock
    request = rf.post(
        reverse("shop:add_to_basket", args=(product.id,)),
        {"quantity": 2, "product_id": variant2.id, "product_type": "shop.ProductVariant"}
    )
    request.session = {"BASKET_ID": basket.id}
    resp = add_to_basket(request, product.id)
    content = resp.content.decode()
    # 6 items now in basket
    assert '<i class="fa-solid fa-basket-shopping"></i>  (6)' in content
    
    # so quantity and +/- buttons hidden
    assert f'id="id_quantity_{product.id}" name="quantity" type="number" value=1' not in content
    assert '<div class="text-danger">Out of stock</div>' in content


def test_add_to_basket_with_error(rf, product):
    # setup empty basket
    request = rf.get('/')
    basket_id = get_basket(request)["id"]
    variant = baker.make(
        "shop.ProductVariant", product=product, variant_name="Small", price=10,
        stock=4
    )
    request = rf.post(
        reverse("shop:add_to_basket", args=(product.id,)),
        {"quantity": 3, "product_id": variant.id, "product_type": "shop.ProductVariant"}
    )
    request.session = {"BASKET_ID": basket_id}

    with mock.patch("shop.views.BasketViewSet.as_view") as mock_basket_as_view:
        class MockResp:
            data = {"quantity": 0}
            status_code = 400

            def __init__(*args, **kwargs):
                ...
        mock_basket_as_view.return_value = MockResp
        resp = add_to_basket(request, product.id)
    content = resp.content.decode()
    assert 'Something went wrong' in content


def test_add_to_basket_cant_increase(rf, product):
    # setup empty basket
    request = rf.get('/')
    basket_id = get_basket(request)["id"]
    # variant with 1 in stock
    variant = baker.make(
        "shop.ProductVariant", product=product, variant_name="Small", price=10,
        stock=1
    )
    # try to add 2 to basked
    request = rf.post(
        reverse("shop:add_to_basket", args=(product.id,)),
        {"quantity": 2, "product_id": variant.id, "product_type": "shop.ProductVariant"}
    )
    request.session = {"BASKET_ID": basket_id}
    resp = add_to_basket(request, product.id)
    content = resp.content.decode()
    # no items in basket
    assert '<i class="fa-solid fa-basket-shopping"></i>  (0)' in content
    assert 'Quantity requested is not available' in content
