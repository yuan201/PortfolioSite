from django import template

register = template.Library()


@register.filter(name='percent')
def percent(value):
    return "{:.1f}%".format(value*100)
