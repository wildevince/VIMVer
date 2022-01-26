
from os import listdir, path, remove

from django.http.response import HttpResponse
from django.shortcuts import render
from django.conf import settings

from OceanViewer.models import Sequence
from .scr import generate3rdline, giveMe_seqArray


# Create your views here.


def home(request, *arg, **kwargv):
    """
    home page

    manage:
        the current selected region
        test the existence of the 2 logos (png format)

    content:
        all Sequences objects
        the select_region form

    render OceanViewer/mapage.html
    """
    #
    kwargv = {
        }

    if Sequence.objects.all():
        refseq = Sequence.objects.get(isRefSeq=True)
        inputSeq = Sequence.objects.get(isRefSeq=False)    

        match_prot = generate3rdline(refseq.prot_seq, inputSeq.prot_seq)
        match_nucl = generate3rdline(refseq.cds_seq, inputSeq.cds_seq, True)
        seq_array = {
            'prot': giveMe_seqArray(refseq.prot_seq, inputSeq.prot_seq, match_prot, 20),
            'nucl': giveMe_seqArray(refseq.cds_seq,  inputSeq.cds_seq,  match_nucl, 60)
            }
        kwargv['seq_array'] = seq_array
        kwargv['refseq'] =  refseq.used_name
        kwargv['inputseq'] =  inputSeq.used_name
        # seq_array kwargv['seq_array']

    return render(request, 'OceanViewer/mapage.html', kwargv)


def delete_all(request):
    """
    delete all Sequences
    """
    Sequence.objects.all().delete()
    dirpath = path.join(settings.MEDIA_ROOT, 'OceanFinder', 'out')
    for file in listdir(dirpath):
        if (file.startswith('in') or file.startswith('out')) and file.endswith('muscle.fasta'):
            remove(path.join(dirpath, file))
    return home(request)


def export(request, filepath):
    ''' download  "outfile.aligned.fasta" '''
    dirpath = path.join(settings.MEDIA_ROOT, 'OceanFinder', filepath)
    if path.exists(dirpath):
        handle = open(dirpath, 'r')
        response = HttpResponse(handle, content_type=dirpath)
        response['Content-Disposition'] = f"attachment; filename={filepath}"
        return response
    return home(request)