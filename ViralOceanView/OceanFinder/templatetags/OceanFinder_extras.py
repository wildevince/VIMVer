from django import template
from django.utils.safestring import mark_safe


register = template.Library()


@register.filter(is_safe=True)
def length(hit):
    return mark_safe(f"{hit['sbjct_end'] - hit['sbjct_start'] +1 }")


@register.filter(is_safe=True)
def match(hit):
    identity = float(hit['identity'])
    length = float(hit['sbjct_end'] - hit['sbjct_start'] +1 )
    return mark_safe(f"{ identity/length *100 : .2f}%")


@register.filter(is_safe=True)
def Len(dico):
    return mark_safe(str(len(dico)))

