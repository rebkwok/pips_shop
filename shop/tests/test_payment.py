from urllib.parse import urlparse, parse_qs

import pytest
from salesman.core.utils import get_salesman_model
from shop.payment import PayInAdvance, PayByStripe


Basket = get_salesman_model("Basket")

Order = get_salesman_model("Order")

pytestmark = pytest.mark.django_db


def test_pay_in_advance(rf, basket):
    basket_id = basket.id
    request = rf.post("/", {"name": "Test buyer"})
    payment = PayInAdvance()
    redirect_url = payment.basket_payment(basket, request)
    assert not Basket.objects.filter(id=basket.id).exists()

    parsed = urlparse(redirect_url)
    token = parse_qs(parsed.query)["token"][0]
    new_order = Order.objects.get(token=token)
    assert new_order.extra == {"basket_id": basket_id}
    assert new_order.status == "HOLD"


def test_pay_by_stripe(requests_mock, rf, basket):
    # mock the stripe requests
    requests_mock.post(
        "https://api.stripe.com/v1/customers", json={"id": "customer-id-1"}
    )
    requests_mock.post(
        "https://api.stripe.com/v1/checkout/sessions", json={"url": "https://stripe-session-url"}
    )

    # Add the extra fields that are added by the checkout serializer when
    # basket is progressed to payment
    basket.extra = {
        "basket_id": basket.id,
        "email": "test@test.com",
        "shipping_address": "-",
        "billing_address": "-",
        "payment_method": "stripe",
    }
    request = rf.post("/", {"name": "Test buyer"})
    payment = PayByStripe()
    redirect_url = payment.basket_payment(basket, request)
    assert redirect_url == "https://stripe-session-url"
    assert basket.extra["name"] == "Test buyer"
    # basket still exists - not deleted  and order not created until the webhook is completed
    assert Basket.objects.filter(id=basket.id).exists()


def test_get_stripe_session_data():
    ...
