from django import template
from django.utils.safestring import mark_safe
from InstantViewer.models import select_region


register = template.Library()


@register.filter(is_safe=True)
def protAsTable(sequence:str, n:int):
    res = ""
    n = int(n)
    for i,residu in enumerate(sequence):
        res += f"<td data-residu='{residu}'"
        if residu == '*':
            res += " mismatch "
        if residu != '_':
            res += f"  data-position={i+n} "
        res += f">{residu}</td>"
    return mark_safe(res)

@register.filter(is_safe=True)
def nuclAsTable(sequence:str, n:int):
    res = ""
    k = 3 
    n = int(n)
    for i,residu in enumerate(sequence):
        if i>0 and i%k==0:
            pos = i//k + n//k
        elif i==0:
            pos = n//k
        res += f"<td data-residu='{residu}'"
        if residu == '*':
            res += " mismatch "
        if residu != '_':
            res += f" data-position={pos+1} "
        res += f">{residu}</td>"
    return mark_safe(res)