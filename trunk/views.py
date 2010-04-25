# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.views.generic.list_detail import object_list, object_detail
from django.views.generic.create_update import create_object, delete_object, \
    update_object
from google.appengine.ext import db
from mimetypes import guess_type

from ragendja.dbutils import get_object_or_404
from ragendja.template import render_to_response


def index(request):
    return  HttpResponseRedirect(reverse('jqchat_test_window', args=[0]))
