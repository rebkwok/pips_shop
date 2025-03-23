from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.template.response import TemplateResponse

from wagtail.models import Page
from wagtail.contrib.search_promotions.models import Query

from shop.models import Product, ProductVariant, CategoryPage

def search(request):
    search_query = request.GET.get("q", None)
    page = request.GET.get("page", 1)

    # Search
    if search_query:
        search_results = Product.objects.filter(live=True, name__icontains=search_query)
        # query = Query.get(search_query)

        # # Record hit
        # query.add_hit()
    else:
        search_results = []

    # Pagination
    paginator = Paginator(search_results, 10)
    try:
        search_results = paginator.page(page)
    except PageNotAnInteger:
        search_results = paginator.page(1)
    except EmptyPage:
        search_results = paginator.page(paginator.num_pages)

    return TemplateResponse(
        request,
        "search/search.html",
        {
            "search_query": search_query,
            "search_results": search_results,
        },
    )
