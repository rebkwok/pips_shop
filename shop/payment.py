# payment.py
from django.conf import settings
from django.urls import path, reverse
from salesman.checkout.payment import PaymentMethod
from salesman_stripe.payment import StripePayment
import stripe

from shop.models import Order


PAYMENT_METHOD_DESCRIPTIONS = {
    "pay-in-advance": """
        Offline payment; your order will be placed on hold until
        payment has been received
    """,
    "stripe": "Pay with stripe",
}

PAYMENT_METHOD_BUTTON_TEXT = {
    "pay-in-advance": "Submit Order",
    "stripe": "Pay Now",
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


class PayByStripe(StripePayment):

    # identifier = "pips-stripe"
    # label = "Pay by Stripe"

    def get_urls(self):
        """
        Register Stripe views.
        """
        return [
            path("cancel/", self.cancel_view, name="stripe-cancel"),
            path("success/?session_id={CHECKOUT_SESSION_ID}", self.success_view, name="stripe-success"),
            path("webhook/", self.webhook_view, name="stripe-webhook"),
        ]

    def basket_payment(self, basket, request):
        return super().basket_payment(basket, request)


    def get_stripe_session_data(
        self, 
        obj, # BasketOrOrder,
        request,
    ):
        """
        Returns Stripe session data to be sent during checkout create.

        See available data to be set in Stripe:
        https://stripe.com/docs/api/checkout/sessions/create
        """

        session_data = super().get_stripe_session_data(obj, request)

        connected_stripe_account_id = settings.STRIPE_CONNECTED_ACCOUNT
        # add in the connect client info
        session_data["payment_intent_data"] = {
            "on_behalf_of": connected_stripe_account_id,
            "transfer_data": {
                "destination": connected_stripe_account_id,
            }
        }
        return session_data

    
    @classmethod
    def cancel_view(cls, request):
        """
        Handle cancelled payment on Stripe.
        """
        # if app_settings.SALESMAN_STRIPE_CANCEL_URL:
        #     return redirect(app_settings.SALESMAN_STRIPE_CANCEL_URL)
        # return render(request, "salesman_stripe/cancel.html")
        return super().cancel_view(request)

    @classmethod
    def success_view(cls, request):
        """
        Handle successfull payment on Stripe.
        """
        checkout_session_id = request.GET.get("session_id")
        session = stripe.checkout.Session.retrieve(checkout_session_id)
        customer = stripe.Customer.retrieve(session.customer)
        import ipdb; ipdb.set_trace()
        # if app_settings.SALESMAN_STRIPE_SUCCESS_URL:
        #     return redirect(app_settings.SALESMAN_STRIPE_SUCCESS_URL)
        # return render(request, "salesman_stripe/success.html")
        return super().success_view(request)
