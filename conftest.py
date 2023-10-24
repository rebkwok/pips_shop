from wagtail.models import Site

import pytest

import wagtail_factories


@pytest.fixture(autouse=True)
def root_page():
    page = wagtail_factories.PageFactory(parent=None)
    Site.objects.create(
        hostname='localhost',
        port=8000,
        root_page=page
    )
    yield page
