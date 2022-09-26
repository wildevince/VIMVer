"""
Copyright. Vincent WILDE (26th September 2022)

vincent.wilde@univ-amu.fr

This software is a computer program whose purpose is to define genonic 
and proteomic mutations between the user's query and the wuhan-1 refseq.

This software is governed by the CeCILL license under French law and
abiding by the rules of distribution of free software.  You can  use, 
modify and/ or redistribute the software under the terms of the CeCILL
license as circulated by CEA, CNRS and INRIA at the following URL
"http://www.cecill.info". 

As a counterpart to the access to the source code and  rights to copy,
modify and redistribute granted by the license, users are provided only
with a limited warranty  and the software's author,  the holder of the
economic rights,  and the successive licensors  have only  limited
liability. 

In this respect, the user's attention is drawn to the risks associated
with loading,  using,  modifying and/or developing or reproducing the
software by the user in light of its specific status of free software,
that may mean  that it is complicated to manipulate,  and  that  also
therefore means  that it is reserved for developers  and  experienced
professionals having in-depth computer knowledge. Users are therefore
encouraged to load and test the software's suitability as regards their
requirements in conditions enabling the security of their systems and/or 
data to be ensured and,  more generally, to use and operate it in the 
same conditions as regards security. 

The fact that you are presently reading this means that you have had
knowledge of the CeCILL license and that you accept its terms.
"""

from django import template
from django.utils.safestring import mark_safe


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
            res += f"  data-position={i+n} title={i+n} "
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
            res += f" data-position={pos+1} title={pos+1} "
        res += f">{residu}</td>"
    return mark_safe(res)