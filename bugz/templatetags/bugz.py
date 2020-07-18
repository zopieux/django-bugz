import hashlib
import urllib.parse

import bleach
import markdown as markdown_
from django import template
from django.conf import settings
from django.template import TemplateSyntaxError
from django.urls import reverse
from django.utils.html import mark_safe

register = template.Library()


@register.filter
def hashed_color(stringable):
    h = hashlib.md5(f"{settings.SECRET_KEY}{stringable}".encode()).digest()
    hue = int.from_bytes(h, byteorder="little") % 360
    return f"hsl({hue},100%,70%)"


@register.filter
def markdown(md: str):
    allowed_tags = bleach.ALLOWED_TAGS + [
        "p",
        "table",
        "thead",
        "tbody",
        "tr",
        "th",
        "td",
    ]
    x = markdown_.markdown(md, extensions=["tables"], output_format="html5")
    y = bleach.clean(x, tags=allowed_tags)
    return mark_safe(y)


@register.simple_tag
def search_url(*kv):
    if len(kv) % 2 != 0:
        raise TemplateSyntaxError(
            "search_url takes an even number of arguments"
        )
    q = " ".join(f"{key}:{value}" for key, value in zip(kv[::2], kv[1::2]))
    return reverse("bugz:home") + "?" + urllib.parse.urlencode({"q": q})


@register.inclusion_tag("bugz/stub-assignee.html")
def show_assignee(assignee):
    return {"assignee": assignee}


@register.inclusion_tag("bugz/stub-author.html")
def show_author(author):
    return {"author": author}


@register.inclusion_tag("bugz/stub-labels.html")
def show_labels(labels):
    return {"labels": labels}


@register.inclusion_tag("bugz/stub-tickets.html")
def show_tickets(tickets):
    from bugz.models import Ticket

    if isinstance(tickets, Ticket):
        tickets = [tickets]
    return {"tickets": tickets}
