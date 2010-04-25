from django.template import Node
from django.template import Library
import  django.template.defaultfilters as defaultfilters
from utils import localtime_for_timezone

register = template.Library()
@register.filter("localtime")
def localtime(value, timezone):
    return localtime_for_timezone(value, timezone)

