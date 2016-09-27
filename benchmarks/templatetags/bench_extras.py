from django import template

register = template.Library()


@register.filter(name='percent')
def percent(value):
    return "{:.1f}%".format(value*100)


@register.filter(name='change')
def change(value):
    return "{:.2f}%".format((value-1)*100)