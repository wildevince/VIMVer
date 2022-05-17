from datetime import datetime
from os import path, remove, listdir
from re import search
from time import sleep

from django.shortcuts import render
from django.views.generic import TemplateView
from django.conf import settings

from .forms import InputForm, JobForm
from .models import Input, Job, OutBlast

from OceanViewer.scr import cutToString, generate_key

from OceanFinder.scr.OceanBlaster import query_to_file, BlastIt, parseOutBlastXml
from OceanFinder.scr.OceanFinder import my_translate


class index(TemplateView):
    template_name = path.join('OceanFinder', 'index.html')

    def get(self, request):
        context = {'input':InputForm(), 'JobForm':JobForm()}
        return render(request, self.template_name, context)


    def post(self, request):
        query = InputForm(request.POST)
        context = {}

        if 'input' in request.POST:
            if query.is_valid():
                
                jobKey = generate_key()
                while len(Job.objects.filter(key = jobKey))>0:
                    jobKey = generate_key()

                query = self.inputFinder(query, jobKey)
                if query == False:
                    context['message'] = "no blast !"
                else:
                    context['query'] = query
                    context['jobKey'] = jobKey
                    context['message'] = "succes"
                context['input'] = InputForm()
                #context['JobForm'] = JobForm()
                return render(request, self.template_name, context)
        
        return index.get(index, request)
        

    def inputFinder(self, inputSequenceForm:InputForm, jobKey:str):
        """inputSequence formular handler.Called when the formular is submited.

        Args:
            inputSequenceForm (inputSequenceForm): response of th formular

        Returns:
            dict: elements from the dict
        """
        #InputFinder.objects.all().delete()   #################
        #Sequence.objects.all().delete()      #################

        inputSequence = str(inputSequenceForm.cleaned_data["sequence"])
        head = inputSequence.split('\n')[0]
        n = head[1:].split()[0]
        seq = inputSequence.split('\n')[1:]

        date = datetime.now().strftime('%d %H')
        job = Job(key= jobKey, date=date)
        ### job: auto_clean
        date_laps = 24 #hours
        d, H = [ int(time_val) for time_val in date.split() ]
        H = d*24 +H
        for item in Job.objects.all():
            #print(item.date)
            item_day, item_Hour = [ int(time_val) for time_val in item.date.split() ]
            item_Hour = item_day*24 +item_Hour
            if item_Hour > H:
                key = item.key
                item.delete()
                dirname = path.join(settings.MEDIA_ROOT,'OceanFinder','out')
                outfiles = [f for f in listdir(dirname) if key == f[:6]]
                for f in outfiles:
                    input(f"removing: {path.join(dirname,f)}")
                    remove(path.join(dirname,f))
        job.save()
        Input(sequence=seq, header=head, name=n, job=job).save()
      
        # run Blast
        queryFile = query_to_file(inputSequence, jobKey)
        queryFilePath = path.join(settings.MEDIA_ROOT,'OceanFinder','out', queryFile)
        #job.queryFasta = path.join(settings.MEDIA_ROOT,'OceanFinder','out', queryFile)
        #job.save(['queryFasta'])
        wait_turn = 0
        while (not path.exists(queryFilePath)) and wait_turn<10:
            wait_turn += 1
            print(f"waited {wait_turn} seconds")
            sleep(1)
        if not path.exists(queryFilePath):
            return False

        blastn = BlastIt(queryFile, jobKey, dated=False)
        blastnPath = path.join(settings.MEDIA_ROOT,'OceanFinder','out', blastn[1])
        #job.outBlastXML = path.join(settings.MEDIA_ROOT,'OceanFinder','out', blastn[1])
        #job.save(['outBlastXML'])
        wait_turn = 0
        while (not path.exists(blastnPath)) and wait_turn<20:
            wait_turn += 1
            print(f"waited {wait_turn} seconds")
            sleep(1)
        if not path.exists(blastnPath):
            return False
    
        #outBlasts = []
        if blastn[0]: 
            job_outBlast = parseOutBlastXml(jobKey) 
            outfileProt = open(path.join(settings.MEDIA_ROOT, 'OceanFinder', 'out', jobKey+'_outfile.prot.fasta'),'w')
            outfileNucl = open(path.join(settings.MEDIA_ROOT, 'OceanFinder', 'out', jobKey+'_outfile.nucl.fasta'),'w')
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
                    job= job,
                    name= n,
                    definition= hit['definition'],
                    accession= hit['accession'],
                    identity= hit['identity'],
                    score=  0 if hit['score']== '???' else hit['score'],
                    sbjct_length= hit['sbjct_length'],
                    hsp_hseq= hit['hsp_hseq'],
                    sbjct_start= hit['sbjct_start'],
                    sbjct_end= hit['sbjct_end'],
                    hsp_qseq= my_inputSequence,
                    query_start= hit['query_start'],
                    query_end= hit['query_end'],
                    qseq_transl= my_inputseq_translate
                ).save()

        return True


class finder(TemplateView):
    template_name = path.join("OceanFinder","finder.html")
        
    def get(self, request):
        jobKey = None
        in_forms = ['key', 'JobKeyForm']
        for in_form in in_forms:
            if in_form in request.GET:
                jobKey = request.GET.get(in_form)

        context = {'JobForm':JobForm()}
        if jobKey:
            job = Job.objects.get(key=jobKey)
            context['job'] = job
            context['jobKey'] = job.key
            context['outBlastList'] = OutBlast.objects.filter(job=job).values()
            context['outfile_nucl_fasta'] = jobKey+"_outfile.nucl.fasta"
            context['outfile_prot_fasta'] = jobKey+"_outfile.prot.fasta"
            return render(request, self.template_name, context)

        context['message'] = "main error !"
        return render(request, self.template_name, context)
        
