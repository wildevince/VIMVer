from datetime import datetime
from os import path
from re import findall, search
from time import sleep

from django.shortcuts import render
from django.views.generic import TemplateView
from django.conf import settings

from .forms import InputForm, JobForm
from .models import Input, Job, OutBlast

from OceanViewer.views import viewer
from OceanViewer.models import Sequence
from OceanViewer.scr import cutToString, generate_key

from OceanFinder.scr.OceanBlaster import query_to_file, BlastIt, parseOutBlastXml, complete
from OceanFinder.scr.OceanFinder import searchRefseq_by_accession, my_translate


class index(TemplateView):
    template_name = path.join('OceanFinder', 'index.html')

    def get(self, request):
        context = {'input': InputForm()}
        return render(request, self.template_name, context)


    def post(self, request):
        query = InputForm(request.POST)
        if 'input' in request.POST:
            if query.is_valid():
                key = generate_key()
                while Job.objects.get(id = key):
                    key = generate_key()
                query = self.inputFinder(query, key)
                context = {'query': query, 'input': InputForm(), 'jobKey': key}
        return render(request, self.template_name, context)
        

    def to_finder(self, request):
        if 'JobKeyForm' in request.POST:
            job = request.POST.get('JobKeyForm')
            return finder.get(request, job)
        ## message ! ERROR
        return index.get(request)


    def inputFinder(self, inputSequenceForm:InputForm, jobKey:str):
        """inputSequence formular handler.Called when the formular is submited.

        Args:
            inputSequenceForm (inputSequenceForm): response of th formular

        Returns:
            dict: elements from the dict
        """
        #InputFinder.objects.all().delete()   #################
        #Sequence.objects.all().delete()      #################

        inputSequenceForm.save()
        inputSequence = str(inputSequenceForm.cleaned_data["Sequence"])
        head = inputSequence.split('\n')[0]
        n = head[1:].split()[0]
        seq = inputSequence.split('\n')[1:]
        query = Input(sequence=seq, header=head, name=n)

        job = Job(
            key= jobKey, 
            query= query.id, 
            date=datetime.now().strftime("-%H%M-%d%m%Y")
            )

        # run Blast
        queryFile = query_to_file(inputSequence)
        job.queryFasta = path.join(settings.MEDIA_ROOT,'OceanFinder','out', queryFile)
        job.save(['queryFasta'])
        sleep(1)

        blastn = BlastIt(queryFile, dated=False)
        job.outBlastXML = path.join(settings.MEDIA_ROOT,'OceanFinder','out', blastn[1])
        job.save(['outBlastXML'])
        sleep(1)

        #outBlasts = []
        if blastn[0]: 
            job_outBlast = parseOutBlastXml(blastn[1]) 
            outfileProt = open(path.join(settings.MEDIA_ROOT, 'OceanFinder', jobKey+'_outfile.prot.fasta'),'w')
            outfileNucl = open(path.join(settings.MEDIA_ROOT, 'OceanFinder', jobKey+'_outfile.nucl.fasta'),'w')
            for hit in job_outBlast:
                outfileProt.write(f">{n}_{hit['name']}\n")
                outfileNucl.write(f">{n}_{hit['name']}\n")
                my_inputSequence = str(hit['hsp_qseq'])
                if search("TTTAAA[C-]CGGG", my_inputSequence[:len(my_inputSequence)//3]):
                    j = my_inputSequence[:len(my_inputSequence)//3].find('A-C') +1
                    inputSequence_corrected = my_inputSequence[:j] + 'A' + my_inputSequence[j+1:]
                    my_inputseq_translate = my_translate(inputSequence_corrected)
                else:
                    my_inputseq_translate = my_translate(my_inputSequence)
                outfileProt.write(''.join(cutToString(my_inputseq_translate)))
                outfileNucl.write(''.join(cutToString(my_inputSequence)))
                # OutBlast
                OutBlast(
                    job= jobKey,
                    name= n,
                    definition= hit['definition'],
                    accession= hit['accession'],
                    identity= hit['identity'],
                    score= hit['score'],
                    sbjct_lenght= hit['sbjct_lenght'],
                    hsp_hseq= hit['hsp_hseq'],
                    sbjct_start= hit['sbjct_start'],
                    sbjct_end= hit['sbjct_end'],
                    hsp_qseq= my_inputSequence,
                    query_start= hit['query_start'],
                    query_end= hit['query_end'],
                    qseq_transl= my_inputseq_translate
                )
                #outBlasts.append(str(hit['accession']))
        #job.outBlast = ' '.join(outBlasts)
        #job.save(['outBlast'])




class finder(TemplateView):
    template_name = path.join("OceanFinder","finder.html")
        
    def get(self, request, **kwargs):
        if 'jobKey' in kwargs:
            jobKey = kwargs['jobKey']
            if jobKey is not None:
                context = { 'JobForm': JobForm, 'job': Job.objects.get(key=jobKey) }
                return render(request, self.template_name, context)
        else :
            render(request, index.template_name)
        
        
    def post(self, request, **kwargs):
        if 'pickBlastRef' in request.POST:
            pick = request.POST.get('pickBlastRef')
            accNbr, jobKey = self.pickBlastRef(pick)
            job = Job.objects.get(key=jobKey)
            context = {'job':job, 'accNbr':accNbr}
            return viewer.get(request, context)
        
        return render(request, index.template_name)
        

    def pickBlastRef(self, pickBlastRefForm, **kwargs):
        blastRef = pickBlastRefForm.split()
        ### BlastRef : "accession jobKey"

        my_refseq = searchRefseq_by_accession(blastRef[0]) #accession 
        ### Caution except my_refSeq = False => search found nothing ???
        if my_refseq is False:
            return (False, "refSeq not found") ######### raise exception : "refSeq not found" !

        #job = Job.objects.get(key=blastRef[1])
        #outBlast_accNbrs = job.outBlast.split()
        outBlast = OutBlast.objects.filter(job=blastRef[1]).values()
        pick_id:int 

        for Hit in outBlast:
            if int(Hit['accession']) == int(my_refseq['accession']):
                inputSequence = Hit['hsp_qseq']
                my_refSeq_sequence = Hit['hsp_hseq']
                pick_id = Hit['id']
                inputName = Hit['name']
                accession = int(my_refseq['accession'])
                break

        # refSeq
        my_refSeq_name = my_refseq['name'] +':'+ my_refseq['header'].split(':')[1]

        # inputSequence

        # check length ?
        length_original = findall(":(\d+)_", my_refseq['header'])[0]
        length_outBlast = len(my_refSeq_sequence)
        if length_original != length_outBlast:
            resMuscle = complete(accNumber= accession)
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
            inputSequence_corrected = inputSequence[:j] + 'A' + inputSequence[j+1:] 
            my_inputseq_translate = my_translate(inputSequence_corrected)

        # export
        with open(path.join(settings.MEDIA_ROOT, 'OceanFinder', blastRef[1]+'_outfile.aligned.fasta'),'w') as handle:
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
        pickBlast.save(['hsp_hseq', 'hseq_transl', 'hsp_qseq', 'qseq_transl'])

        # InputFinder.objects.all().delete()
        # preparing alignemnt
        if not Sequence.objects.filter(job=blastRef[1]):
            Sequence(used_name=my_refSeq_name, isRefSeq=True, job=blastRef[1],
                prot_seq=str(my_refSeq_translate), cds_seq=my_refSeq_sequence).save()
            Sequence(used_name=str(inputName), job=blastRef[1], prot_seq=str(my_inputseq_translate), cds_seq=inputSequence).save()
        return (accession, blastRef[1])

