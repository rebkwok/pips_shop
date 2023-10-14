from django.http import HttpRequest
from salesman.basket.models import BaseBasket
from salesman.basket.modifiers import BasketModifier


class ShippingCostModifier(BasketModifier):
    """
    Add flat shipping cost to the basket.
    """

    identifier = "shipping-cost"

    def process_basket(self, basket, request):
        if basket.shipping_method != "collect" and basket.count:
            self.add_extra_row(basket, request, label="Shipping", amount=3.99)
