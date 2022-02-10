from django import forms
from .models import Sequence
from .scr import re_align

class SequenceForm(forms.ModelForm):
    """
    ModelForm
    parsing the Sequence Model:
        - remove all blank characters
        - check for CDS sequence
    """
    class Meta:
        model = Sequence
        fields = ('accNbr_gb','used_name','prot_seq', 'cds_seq')

    def clean_prot_seq(self):
        """ remove all blank characters """
        prot_seq = ''.join(self.cleaned_data["prot_seq"].split())
        return prot_seq

    def clean_cds_seq(self):
        """
        remove all blank characters
        check for CDS sequence
        """
        cds_seq = self.cleaned_data.get('cds_seq')
        prot_seq = ''.join(self.cleaned_data.get('prot_seq'))
        cds_seq = ''.join(cds_seq.split())
        return re_align(prot_seq, cds_seq)
