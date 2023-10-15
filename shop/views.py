from datetime import datetime
from urllib.parse import parse_qsl, urlparse, urlunparse
import logging

import requests
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.generic import DetailView
from salesman.basket.views import BasketViewSet
from salesman.checkout.views import CheckoutViewSet
from salesman.core.utils import get_salesman_model

from .forms import CheckoutForm
from .models import ProductCategory, ProductVariant, Product, SHIPPING_METHODS
from .payment import PAYMENT_METHOD_DESCRIPTIONS


logger = logging.getLogger(__name__)

Basket = get_salesman_model("Basket")


def get_basket(request):
    request.method = "GET"
    resp = BasketViewSet.as_view({"get": "list"})(request)
    return resp.data


def get_basket_quantity(request):
    request.method = "GET"
    resp = BasketViewSet.as_view({"get": "quantity"})(request)
    return resp.data["quantity"]


def get_basket_total(request):
    return get_basket(request)["total"]


def get_basket_quantity_and_total(request):
    return get_basket_quantity(request), get_basket(request)["total"]


class ProductCategoryDetailView(DetailView):
    model = ProductCategory
    template_name = "shop/shop_category_page.html"
    context_object_name = "category"


class ProductDetailView(DetailView):
    model = Product
    template_name = "shop/shop_product_page.html"
    context_object_name = "product"


def decrease_quantity(request, product_id):        
    value = int(request.GET.get("quantity", 1))
    if value > 1:
        value -= 1
    return _change_quantity(request, product_id, value)


def get_basket_item(basket, product_id):
    if not basket["items"]:
        return {}
    return next(
        (item for item in basket["items"] if int(item["product_id"]) == int(product_id)),
        {}
    )

def can_increase_quantity(request, variant, value, in_basket=False):
    # value is the amount we want to increase TO
    if in_basket:
        # increasing a value from the basket; current basket quantity 
        # is already incorporated into stock numbers
        # we need to check the actual basket quantity because user may have increase/decreased
        # value in the form field without actually updating
        current_quantity = get_basket_item(get_basket(request), variant.id).get("quantity", 0)
        logger.info("Current quantity %s", current_quantity)
        logger.info("Stock %s", variant.stock)
        logger.info("New quantity %s", variant.stock)
        stock_excluding_current_basket = variant.stock + current_quantity
        return (stock_excluding_current_basket - value) >= 0
    else:
        return (variant.stock - value) >= 0

def increase_quantity(request, product_id):
    variant = ProductVariant.objects.get(id=int(product_id))
    value = int(request.GET.get("quantity", 1))
    in_basket = request.GET.get("ref") == "basket"
    # We click on this to increase the quantity from its current value
    # check that we can increase to this value plus 1
    can_increase = can_increase_quantity(request, variant, value + 1, in_basket)
    if can_increase:
        value += 1
    return _change_quantity(request, product_id, value, can_increase=can_increase)


def _change_quantity(request, product_id, new_value, can_increase=True):
    context = {"product_id": product_id, "value": new_value}
    resp_str = render_to_string("shop/includes/quantity_field.html", context, request)
    resp_str += f"""
        <div id='added_{product_id}' hx-swap-oob='true'></div>
        <div id='updated_{product_id}' hx-swap-oob='true'></div>
    """
    if not can_increase:
        resp_str += (
            f"<div id='updated_{product_id}' class='alert-info' hx-swap-oob='true'>"
            "Can't increase quantity</div>"
        )
        resp = HttpResponse(resp_str)
        return resp
    resp = HttpResponse(resp_str)
    resp.headers['HX-Trigger'] = "quantity-changed"
    return resp


def add_to_basket(request, product_id):
    variant = ProductVariant.objects.get(id=product_id)
    # check we can increase

    # add_to_basket is called from the shop page, not the basket page; we're
    # adding this entire quantity to the basket, but we're not incrementing 
    # it, so just check we can add the current quantity
    can_increase = can_increase_quantity(
        request, variant, int(request.POST.get("quantity")), in_basket=False
    )        
    
    if can_increase:
        resp = BasketViewSet.as_view({"post": "create"})(request)
        new_basket_quantity = get_basket_quantity(request)
        resp_str = f"<div>{_basket_icon_html(request, new_basket_quantity)}</div>"
        if resp.status_code == 201:
            resp_str += f"""
                <div id='added_{product_id}' class='alert-success mt-2' hx-swap-oob='true'>Added!</div>
            """
            if variant.product.out_of_stock():
                resp_str += "<div id='change_quantity_wrapper' hx-swap-oob='true'></div>"
            else:
                # update variant dropdown
                variant_html = render_to_string(
                    "shop/includes/select_variant_field.html", {"product": variant.product, "product_id": product_id}, request
                )
                # set quantity back to 1
                quantity_to_add_html = render_to_string(
                    "shop/includes/quantity_field.html", {"product_id": product_id, "value": 1}, request
                    )
                resp_str += f"""
                    <div id='id_quantity_wrapper_{ product_id }' hx-swap-oob='true'>{quantity_to_add_html}</div>
                    <div id='id_select_variant_wrapper_{ product_id }' hx-swap-oob='true'>{variant_html}</div>
                """
        else:
            logger.error("Error adding to basket: status_code %s resp %s", resp.status_code, resp.data)
            resp_str += f"""
                <div id='added_{product_id}' class='alert-danger mt-2' hx-swap-oob='true'>Something went wrong</div>
                """
    else:
        logger.error("Error adding to basket: can't increase quantity %r", get_basket(request))
        basket_quantity = get_basket_quantity(request)
        resp_str = f"<div>{_basket_icon_html(request, basket_quantity)}</div>"
        resp_str += f"""
        <div id='added_{product_id}' class='alert-danger mt-2' hx-swap-oob='true'>Something went wrong</div>
        """
    
    return HttpResponse(resp_str)


def update_quantity(request, ref):
    product_id = int(request.POST.get("product_id"))
    request.method = "GET"
    current_item_resp = BasketViewSet.as_view({"get": "retrieve"})(request, ref=ref)

    if current_item_resp.data["quantity"] == int(request.POST.get("quantity")):
        # nothing to do
        result_html = (
            f"<div id='updated_{product_id}' class='alert-info' hx-swap-oob='true'></div>"
        )
    else:
        request.method = "PUT"
        resp = BasketViewSet.as_view({"put": "update"})(request, ref=ref)

        if resp.status_code != 200:
            result_html = f"<div id='updated_{product_id}' class='alert-danger' hx-swap-oob='true'>Error</div>"
        else:
            basket = get_basket(request)
            basket_extra_html = render_to_string(
                "shop/includes/basket_extra.html",
                {"extra_rows": basket["extra_rows"]},
                request,
            )
            subtotal = get_basket_item(basket, product_id).get("subtotal", 0)
            result_html = f"""
                <span id='subtotal_{product_id}' hx-swap-oob='true'>{subtotal}</span>
                <span id='quantity_{product_id}' hx-swap-oob='true'>{resp.data['quantity']}</span>
                <span id='total' hx-swap-oob='true'>{basket['total']}</span>
                <div id='updated_{product_id}' class='alert-success' hx-swap-oob='true'>Basket updated</div>
                <div id='basket-extra' class='col-md-12' hx-swap-oob='true'>{basket_extra_html}</div>
            """
    return HttpResponse(result_html)


def delete_basket_item(request, ref):
    product_id = int(request.POST.get("product_id"))

    request.method = "DELETE"
    product_identifier = ProductVariant.objects.get(id=product_id).product.identifier
    resp = BasketViewSet.as_view({"delete": "destroy"})(request, ref=ref)

    if resp.status_code != 204:
        resp_str = f"""
            <div id='updated_{product_id}' class='alert-danger' hx-swap-oob='true'>Error</div>
        """
    else:
        request.method = "GET"
        new_basket_quantity = get_basket_quantity(request)
        basket = get_basket(request)
        any_products = any(
            1
            for item in basket["items"]
            if ProductVariant.objects.get(id=item["product_id"]).product.identifier
            == product_identifier
        )

        if not any_products:
            resp_str = f"<div id='row-{product_identifier}' hx-swap-oob='true'></div>"
        else:
            resp_str = f"<div id='row-{product_id}' hx-swap-oob='true'></div>"

        if new_basket_quantity == 0:
            resp_str += "<div id='basket-total-and-payment' hx-swap-oob='true'><p>Basket is empty.</p></div>"
        else:
            resp_str += f"<span id='total' hx-swap-oob='true'>{basket['total']}</span>"

        basket_extra_html = render_to_string(
            "shop/includes/basket_extra.html",
            {"extra_rows": basket["extra_rows"]},
            request,
        )
        resp_str += f"<div id='basket-extra' class='col-md-12' hx-swap-oob='true'>{basket_extra_html}</div>"
    return HttpResponse(resp_str)


def _basket_icon_html(request, quantity):
    return render_to_string(
        "shop/includes/basket_icon.html", {"basket_quantity": quantity}, request
    )


def basket_view(request):
    resp = BasketViewSet.as_view({"get": "list"})(request)
    basket_context = get_basket_context(resp.data)
    checkout_methods = CheckoutViewSet.as_view({"get": "list"})(request)
    payment_methods = checkout_methods.data["payment_methods"]
    shipping_methods = [("collect", "Collect in store"), ("deliver", "Delivery")]
    for method in payment_methods:
        method["help"] = PAYMENT_METHOD_DESCRIPTIONS[method["identifier"]]
    return render(
        request,
        "shop/basket.html",
        {**basket_context, "payment_methods": payment_methods, "shipping_methods": shipping_methods, "hide_basket": True},
    )


def get_basket_context(basket):
    basket_quantity = _get_basket_quantity(basket)
    items_by_product = {}
    for item in basket.get("items", []):
        product_type = ProductVariant.objects.get(id=item["product_id"]).product
        item["product_type"] = product_type.name
        item["category"] = product_type.category
        items_by_product.setdefault(product_type.identifier, []).append(item)
    basket["items"] = items_by_product
    return {"basket": basket, "basket_quantity": basket_quantity}


def _get_basket_quantity(basket):
    return sum(int(item["quantity"]) for item in basket.get("items", []))


def checkout_view(request):
    payment_method = request.GET["payment-method"]
    shipping_method = request.GET["shipping-method"]
    context = {"payment_method": payment_method, "shipping_method": shipping_method}
    
    if request.method == "POST":

        form = CheckoutForm(payment_method=payment_method, shipping_method=shipping_method, data=request.POST)

        if form.is_valid():
            checkout = CheckoutViewSet.as_view({"post": "create"})(request)

            if checkout.status_code == 201:
                if payment_method == "stripe":
                    return HttpResponseRedirect(checkout.data["url"])

                parsed_url = urlparse(checkout.data["url"])
                token = dict(parse_qsl(parsed_url.query))["token"]
                return HttpResponseRedirect(
                    reverse("shop:new_order_status", args=(token,))
                )
            context["checkout_error"] = True
    else:
        # update basket with shipping method
        basket = Basket.objects.get(id=get_basket(request)["id"])
        basket.shipping_method = shipping_method
        basket.save()
        form = CheckoutForm(payment_method=payment_method, shipping_method=shipping_method)

    request.method = "GET"
    resp = BasketViewSet.as_view({"get": "list"})(request)
    context = {**context, "form": form, **get_basket_context(resp.data)}

    return render(request, "shop/checkout.html", context)


def new_order_view(request, token):
    return _order_status(request, token, new=True)


def order_status_view(request, token):
    return _order_status(request, token)


def _order_status(request, token, new=False):
    parsed = urlparse(request.build_absolute_uri())
    url = urlunparse(
        (
            parsed.scheme,
            parsed.netloc,
            "/api/orders/last/",
            "",
            f"token={token}&format=json",
            "",
        )
    )
    resp = requests.get(url)
    order = resp.json()
    order["date_created"] = datetime.strptime(
        order["date_created"], "%Y-%m-%dT%H:%M:%S.%fZ"
    )
    order = get_basket_context(order)["basket"]
    shipping_method = SHIPPING_METHODS[order["shipping_method"]]
    context = {"order": order, "new_order": new, "hide_basket": True, "shipping_method": shipping_method}
    return render(request, "shop/order_status.html", context)
