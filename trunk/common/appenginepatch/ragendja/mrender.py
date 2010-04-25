# -*- coding: utf-8 -*-
from django.http import HttpResponse
from Cookie import SimpleCookie
from django.conf import settings
#from ragendja.template import render_to_string;
from django.template.loader import render_to_string as rts;

class GbkHttpResponse(HttpResponse):
    """
                return gbk encoding response
    """
    status_code = 200
    def __init__(self, content='', mimetype=None, status=None, content_type=None):
        self._charset = 'gbk'
        content_type = "text/html; charset=gbk"
        if not isinstance(content, basestring) and hasattr(content, '__iter__'):
            self._container = content
            self._is_string = False
        else:
            self._container = [content]
            self._is_string = True
        self.cookies = SimpleCookie()
        self._headers = {'content-type': ('Content-Type', content_type)}

        
def render_to_response(*args, **kwargs):
    """
    Returns a HttpResponse whose content is filled with the result of calling
    django.template.loader.render_to_string() with the passed arguments.
    """
    httpresponse_kwargs = {'mimetype': kwargs.pop('mimetype', None)}
    return GbkHttpResponse(rts(*args, **kwargs), **httpresponse_kwargs)
    

"""    
def render_to_response( template_name , data, extradata=None, mimetype=None):
    request = data;
    if mimetype is None:
        mimetype = settings.DEFAULT_CONTENT_TYPE
    original_mimetype = mimetype
    if mimetype == 'application/xhtml+xml':
        # Internet Explorer only understands XHTML if it's served as text/html
        if request.META.get('HTTP_ACCEPT').find(mimetype) == -1:
            mimetype = 'text/html'

    response = GbkHttpResponse(render_to_string(request, template_name, data),
        content_type='%s; charset=%s' % (mimetype, settings.DEFAULT_CHARSET))
    
    if original_mimetype == 'application/xhtml+xml':
        # Since XHTML is served with two different MIME types, depending on the
        # browser, we need to tell proxies to serve different versions.
        from django.utils.cache import patch_vary_headers
        patch_vary_headers(response, ['User-Agent'])

    return response

"""