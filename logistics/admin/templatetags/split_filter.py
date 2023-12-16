from django import template
register = template.Library()
@register.filter(name='split')
def split(value, key):
    """
        Returns the value turned into a list.
    """
    return value.split(key)

@register.filter(name='sub')
def sub(val1, val2):
    """
        Returns the value turned into a list.
    """
    return val1-val2