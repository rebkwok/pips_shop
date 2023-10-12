# payment.py
from django.urls import reverse
from salesman.checkout.payment import PaymentMethod

from shop.models import Order


PAYMENT_METHOD_DESCRIPTIONS = {
    "pay-in-advance": """
        Offline payment; your order will be placed on hold until
        payment has been received
    """,
}

PAYMENT_METHOD_BUTTON_TEXT = {
    "pay-in-advance": "Submit Order",
}


class PayInAdvance(PaymentMethod):
    """
    Payment method that requires advance payment via bank account.
    """

    identifier = "pay-in-advance"
    label = "Pay in advance"

    def basket_payment(self, basket, request):
        """
        Create a new order and mark it on-hold. Reserve items from stock and await
        manual payment from customer via back account. When paid order status should be
        changed to `PROCESSING`, `SHIPPED` or `COMPLETED` and a new payment should be
        added to order.
        """
        basket.extra["name"] = request.POST.get("name")
        basket.save()
        order = Order.objects.create_from_basket(basket, request, status="HOLD")
        basket.delete()
        url = reverse("salesman-order-last") + f"?token={order.token}"
        return request.build_absolute_uri(url)
