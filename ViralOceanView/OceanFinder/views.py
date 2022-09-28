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
    """ 1st page requests """
    template_name = path.join('OceanFinder', 'index.html')
    creation_limiter = 2

    def get(self, request):
        context = {'input':InputForm(), 'JobForm':JobForm()}
        return render(request, self.template_name, context)


    def post(self, request):
        """ user's sequence submission """
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
        def clean_old_jobs():
            index.creation_limiter = 2
            outPath = path.join(settings.MEDIA_ROOT,'OceanFinder','out')
            date = datetime.now().strftime('%d %H')
            date = date.split()
            #date = { 'day':data[0], 'hour':data[1] }
            for job in Job.objects.all():
                jobkey = job.key
                job_day, job_hour = job.date.split()
                time = 24 * (int(date[0])- int(job_day))
                time += (int(date[1]) - int(job_hour))
                #timeUp = ""
                print(job.key, job.date)
                if(time >= 1):  # 24 hours
                    #timeUp = "*"
                    print("deleting", job.key)
                    job.delete()
                    for file in listdir(outPath):
                        if(path.basename(file).startswith(jobkey)):
                            remove(file)

                    ###############################
                    ###############################
                    

            ### job: auto_clean
            
        

        inputSequence = str(inputSequenceForm.cleaned_data["sequence"])
        head = inputSequence.split('\n')[0]
        n = head[1:].split()[0]
        seq = inputSequence.split('\n')[1:]

        date = datetime.now().strftime('%d %H')
        job = Job(key= jobKey, date=date)
        index.creation_limiter -= 1
        job.save()
        if(index.creation_limiter <= 0):  # auto-clean every creation_limiter Job created
            clean_old_jobs()
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
                    inputSequence_corrected = my_inputSequence[:j] + 'C' + my_inputSequence[j+1:]
                    my_inputseq_translate = my_translate(inputSequence_corrected)
                else:
                    my_inputseq_translate = my_translate(my_inputSequence)
                outfileProt.write(''.join(cutToString(my_inputseq_translate)))
                outfileNucl.write(''.join(cutToString(my_inputSequence)))
                # OutBlast
                OutBlast(
                    job= job,
                    name= f"{n}_{hit['name']}",
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
    """ 2nd page: results form blast """
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
        
