from django import template

register = template.Library()


# 将url参数更新并整合在一起
@register.simple_tag
def query_transform(request, **kwargs):
    url_params = request.GET.copy()
    for k, v in kwargs.items():
        if v is None:
            url_params.pop(k, 0)
        else:
            url_params[k] = v

    return url_params.urlencode()
