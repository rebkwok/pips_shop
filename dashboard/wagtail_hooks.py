from django.urls import reverse
from django.utils.safestring import mark_safe
from wagtail import hooks
from wagtail.admin.menu import MenuItem
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from home.models import FooterText



class FooterTextViewSet(SnippetViewSet):
    model = FooterText
    search_fields = ("body",)
    add_to_admin_menu = True
    menu_label = "Footer Text"
    menu_order = 400  # will put in 5th place (000 being 1st, 100 2nd)


@hooks.register('register_admin_menu_item')
def register_collections_menu_item():
  return MenuItem('Collections', reverse('wagtailadmin_collections:index'), icon_name='folder-inverse', order=300)


register_snippet(FooterTextViewSet)
