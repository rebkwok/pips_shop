from django.urls import reverse

import pytest


pytestmark = pytest.mark.django_db


def test_search_view(home_page, client):
    resp = client.get(reverse("search") + "?query=home")
    assert resp.context_data["search_query"] == "home"
    assert [pg.id for pg in resp.context_data["search_results"].object_list] == [
        home_page.id
    ]


def test_search_view_no_query(home_page, client):
    resp = client.get(reverse("search"))
    assert resp.context_data["search_query"] == None
    assert [pg.id for pg in resp.context_data["search_results"].object_list] == []


def test_search_view_no_match(home_page, client):
    resp = client.get(reverse("search") + "?query=foo")
    assert resp.context_data["search_query"] == "foo"
    assert [pg.id for pg in resp.context_data["search_results"].object_list] == []


@pytest.mark.parametrize("page", ["not-a-page", "9", ""])
def test_search_view_paginator(home_page, client, page):
    resp = client.get(reverse("search") + f"?query=home&page={page}")
    assert [pg.id for pg in resp.context_data["search_results"].object_list] == [
        home_page.id
    ]
