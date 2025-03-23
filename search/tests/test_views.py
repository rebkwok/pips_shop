from django.urls import reverse

import pytest


pytestmark = pytest.mark.django_db


def test_search_view(product, client):
    resp = client.get(reverse("search") + "?q=test")
    assert resp.context_data["search_query"] == "test"
    assert [pd.id for pd in resp.context_data["search_results"].object_list] == [
        product.id
    ]


def test_search_view_no_query(product, client):
    resp = client.get(reverse("search"))
    assert resp.context_data["search_query"] == None
    assert [pd.id for pd in resp.context_data["search_results"].object_list] == []


def test_search_view_no_match(product, client):
    resp = client.get(reverse("search") + "?q=foo")
    assert resp.context_data["search_query"] == "foo"
    assert [pd.id for pd in resp.context_data["search_results"].object_list] == []


@pytest.mark.parametrize("page", ["not-a-page", "9", ""])
def test_search_view_paginator(product, client, page):
    resp = client.get(reverse("search") + f"?q=test&page={page}")
    assert [pd.id for pd in resp.context_data["search_results"].object_list] == [
        product.id
    ]
