from wagtail.models import Site

import pytest

import wagtail_factories


pytestmark = pytest.mark.django_db


class HomePageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = "home.HomePage"


@pytest.fixture
def home_page(autouse=True):
    root_page = wagtail_factories.PageFactory(parent=None)
    page = HomePageFactory(
        parent=root_page, title="Home", hero_text="Home", hero_cta="Test", body="Test",
    )
    Site.objects.create(
        hostname='localhost',
        port=8000,
        root_page=page,
        is_default_site=True,
    )
    yield page
