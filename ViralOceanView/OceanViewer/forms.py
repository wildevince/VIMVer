from django import forms
from .models import Sequence
from .scr import re_align, get_CDS, get_nucl_accNbr


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
        AccNub = self.cleaned_data.get('accNbr_gb')
        cds_seq = self.cleaned_data.get('cds_seq')
        if (not cds_seq) and (AccNub):
            other = get_nucl_accNbr(AccNub)
            cds_seq = ''.join(get_CDS(other)['sequence'].split())
            # cds_seq = cds_seq.encode('ASCII')
        elif not (AccNub or cds_seq):
            raise forms.ValidationError(
                        "Warning: please give the genbank accession number \
                        or the raw cds sequence, for each entity.")
        prot_seq = ''.join(self.cleaned_data.get('prot_seq'))
        cds_seq = ''.join(cds_seq.split())
        return re_align(prot_seq, cds_seq)


