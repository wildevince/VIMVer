
from os import path

from django.http.response import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView
from django.conf import settings

from .models import Sequence
from .scr import generate3rdline, giveMe_seqArray

from OceanFinder.forms import JobForm
from OceanFinder.models import Job
#from OceanFinder.views import index


# Create your views here.

class viewer(TemplateView):
    template_name = path.join('OceanViewer', 'viewer.html')

    def get(self, request, **kwargs):
        if 'jobKey' in kwargs:
            jobKey = kwargs['jobKey']
            context = {'JobForm':JobForm}
            context['job'] = Job.objects.get(id=jobKey)
            sequences = Sequence.objects.filter(job=jobKey)
            if len(sequences)>0:
                refseq = sequences.get(isRefSeq=True)
                inputSeq = sequences.get(isRefSeq=False)   
                match_prot = generate3rdline(refseq.prot_seq, inputSeq.prot_seq)
                match_nucl = generate3rdline(refseq.cds_seq, inputSeq.cds_seq, True)
                seq_array = {
                    'prot': giveMe_seqArray(refseq.prot_seq, inputSeq.prot_seq, match_prot, 20),
                    'nucl': giveMe_seqArray(refseq.cds_seq,  inputSeq.cds_seq,  match_nucl, 60)
                    }
                
                context['seq_array'] = seq_array
                context['refseq'] =  refseq.used_name
                context['inputseq'] =  inputSeq.used_name
                return render(request, viewer.template_name, context)
            #else: 
                # raise exception : job not found !

        return render(request, "OceanViewer/viewer.html", {'JobForm':JobForm()})  #index.get(request)
        

    #def post(self, request, **kwargs):
    #    context = {'JobForm':JobForm}


    #def to_viewer(self, request, **kwargs):
    #    viewer.get(request, kwargs)


def export(request, filepath):
    ''' download  "outfile.aligned.fasta" '''
    dirpath = path.join(settings.MEDIA_ROOT, 'OceanFinder', filepath)
    if path.exists(dirpath):
        handle = open(dirpath, 'r')
        response = HttpResponse(handle, content_type=dirpath)
        response['Content-Disposition'] = f"attachment; filename={filepath}"
        return response
    return viewer.get(viewer, request)