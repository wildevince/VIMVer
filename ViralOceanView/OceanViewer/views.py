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


from os import path
from re import findall, search

from django.http.response import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView
from django.conf import settings

from .models import Sequence
from .scr import generate3rdline, giveMe_seqArray, cutToString

from OceanFinder.forms import JobForm
from OceanFinder.models import Job, OutBlast

from OceanFinder.scr.OceanBlaster import complete
from OceanFinder.scr.OceanFinder import searchRefseq_by_accession, my_translate



# Create your views here.

class viewer(TemplateView):
    """ 3rd page """
    template_name = path.join('OceanViewer', 'viewer.html')

    def get(self, request):
        """ load 'picked' alignment """
        context = {'JobForm':JobForm()}

        if 'pickBlastRef' in request.GET:
            accession, jobKey = request.GET.get('pickBlastRef').split()
            res = self.pickBlastRef(accession, jobKey)
            job = Job.objects.get(key=jobKey)
            context['job'] = job
            if res[0] == False:
                context['message'] = "pick ref blast : failed"
            else: 
                sequences = Sequence.objects.filter(job=job)
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
                context['outfile_aligned_fasta'] = jobKey+"_outfile.aligned.fasta"
                return render(request, viewer.template_name, context)
                
        return render(request, viewer.template_name, context) 
        

    def pickBlastRef(self, accession, jobKey):
        """ called in viewer.get : preparing and running the alignment """

        my_refseq = searchRefseq_by_accession(accession) 
        ### Caution except my_refSeq = False => search found nothing ???
        if my_refseq is False:
            return (False, "refSeq not found") ######### raise exception : "refSeq not found" !

        job = Job.objects.get(key=jobKey)
        hit = OutBlast.objects.filter(job=job, accession=accession)
        if not hit:
            return (False, "OutBlast : hit not found")
        elif len(hit)>1 :
            return (False, "Queryset: lacking specificity")
        hit = hit[0]
        pick_id = hit.id
        inputSequence = str(hit.hsp_qseq)
        my_refSeq_sequence = str(hit.hsp_hseq)
        inputName = str(hit.name)

        # refSeq
        my_refSeq_name = my_refseq['name'] +':'+ my_refseq['header'].split(':')[1]

        # check length ?
        length_original = findall(":(\d+)_", my_refseq['header'])[0]
        length_outBlast = len(my_refSeq_sequence)
        if length_original != length_outBlast:
            resMuscle = complete(accNumber= accession, jobKey= jobKey)
            inputSequence = str(resMuscle['hsp_qseq'])
            my_refSeq_sequence = str(resMuscle['hsp_hseq'])
        ##
        my_refSeq_translate = my_translate(my_refSeq_sequence)
        my_inputseq_translate = my_translate(inputSequence)

        # frameshift ?
        score = 0
        score += -1 if len(my_refSeq_translate) == len(my_inputseq_translate) else 1
        k = 0
        l = min([len(my_inputseq_translate), len(my_refSeq_translate)])
        while my_inputseq_translate[k] == my_refSeq_translate[k]:
            k +=1
            if k >= l:
                break 
        k -=1
        score += 1 if k in range(8-1, 8+1) else 0
        score += 3 if my_refSeq_translate.startswith("SADAQ") and my_inputseq_translate.startswith("SADAQ") else -1
        res = search("TTTAAA[C-]CGGG", my_refSeq_sequence[:len(my_inputseq_translate)])
        score += 3 if res else -1
        if score >= 5 :
            j = inputSequence[:len(inputSequence)//3].find("A-C") +1
            inputSequence_corrected = inputSequence[:j] + 'C' + inputSequence[j+1:] 
            my_inputseq_translate = my_translate(inputSequence_corrected)

        # export
        with open(path.join(settings.MEDIA_ROOT, 'OceanFinder','out', jobKey+'_outfile.aligned.fasta'),'w') as handle:
            handle.write(f">{my_refSeq_name}_nucl\n")
            handle.write(''.join(cutToString(my_refSeq_sequence))) 
            handle.write(f">{my_refSeq_name}_prot\n")
            handle.write(''.join(cutToString(my_refSeq_translate))) 
            handle.write(f">{inputName}_nucl\n")
            handle.write(''.join(cutToString(inputSequence))) 
            handle.write(f">{inputName}_prot\n")
            handle.write(''.join(cutToString(my_inputseq_translate))) 

        # update OutBlast !
        pickBlast = OutBlast.objects.get(id=pick_id)
        pickBlast.hsp_hseq = my_refSeq_sequence
        pickBlast.hseq_transl = my_refSeq_translate
        pickBlast.hsp_qseq = inputSequence
        pickBlast.qseq_transl = my_inputseq_translate
        pickBlast.save()
        
        # InputFinder.objects.all().delete()
        # preparing alignemnt
        if not Sequence.objects.filter(job=job):
            Sequence(used_name=my_refSeq_name, isRefSeq=True, job=job,
                prot_seq=str(my_refSeq_translate), cds_seq=my_refSeq_sequence).save()
            Sequence(used_name=str(inputName), job=job, prot_seq=str(my_inputseq_translate), cds_seq=inputSequence).save()
        return (True, "succes")


def export(request, filepath):
    ''' download  "outfile.aligned.fasta" '''
    dirpath = path.join(settings.MEDIA_ROOT, 'OceanFinder', 'out', filepath)
    if path.exists(dirpath):
        handle = open(dirpath, 'r')
        response = HttpResponse(handle, content_type=dirpath)
        response['Content-Disposition'] = f"attachment; filename={filepath}"
        return response
    return viewer.get(viewer, request)