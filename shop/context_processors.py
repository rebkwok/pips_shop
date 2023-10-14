from .views import get_basket_quantity

def shop_context(request):
    return {
        "basket_quantity": get_basket_quantity(request)
    }
