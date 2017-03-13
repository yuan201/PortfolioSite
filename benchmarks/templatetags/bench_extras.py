from django import template

register = template.Library()


@register.filter(name='percent')
def percent(value):
    if isinstance(value, float):
        return "{:.1f}%".format(value*100)
    else:
        return ""


@register.filter(name='change')
def change(value):
    if isinstance(value, float):
        return "{:.2f}%".format((value-1)*100)
    else:
        return ""