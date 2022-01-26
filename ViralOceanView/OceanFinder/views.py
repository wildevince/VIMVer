from os import path
from re import findall, search
from time import sleep

from django.shortcuts import render
from django.views.generic import TemplateView
from django.conf import settings

from .forms import InputFinderForm
from .models import InputFinder

from OceanViewer.views import home
from OceanViewer.models import Sequence
from OceanViewer.scr import cutToString

from OceanFinder.scr.OceanBlaster import query_to_file, BlastIt, parseOutBlastXml, complete
from OceanFinder.scr.OceanFinder import searchRefseq_by_accession, my_translate



class index(TemplateView):

    template_name = path.join("OceanFinder","index.html")
    _outBlast = []
    
    
    def outBlast(self, arg=[]):
        if arg:
            index._outBlast = arg
        else :
            return index._outBlast


    def get(self, request, **kwargs):
        #print('GET')  ###
        #print(f"\t*BlastRef.outBlastList lenght: {len(BlastRef.outBlastList)}")

        InputFinder.objects.all().delete()
        # Sequence.objects.all().delete()
        # BlastRef.outBlastList = []
        kwargs['inputSequenceForm'] = InputFinderForm()
        
        return render(request, self.template_name, kwargs)
        

    def post(self, request, **kwargs):
        #print('POST')  ###
        
        #print(f"\t*post kwargs: {' '.join([key for key in kwargs])}")

        inputSequenceForm = InputFinderForm(request.POST or None)
        kwargs['inputSequenceForm'] = inputSequenceForm
        
        ### check
        #print(f"\t*outBlastList lenght: {len(self.outBlast())}")
        #for hit in self.outBlast():
            #print(f"\t\t-accession: {hit['accession']}\t-score: {hit['score']}")

        if 'inputFinder' in request.POST:
            if inputSequenceForm.is_valid():
                #print('\tPOST inputSequence')  ###
                self.inputFinder(inputSequenceForm)
                kwargs['outBlastList'] = self.outBlast()
                #kwargs['message'] = "includes pineapples !"
                kwargs['inputSequence'] = str(InputFinder.objects.all()[0].inputSequence)
                #print(f"=>input seq header: {kwargs['inputSequence'].split()[0]}")
                
        elif 'pickBlastRef' in request.POST:
            self.pickBlastRef(request.POST.get('pickBlastRef'))
            #print(f"\t=>home kwargs: {' '.join([key for key in kwargs])}")
            return home(request)
        
        #print(f"\t=>render kwargs: {' '.join([key for key in kwargs])}")
        return render(request, self.template_name, kwargs)
        
    
    def inputFinder(self, inputSequenceForm):
        """inputSequence formular handler.Called when the formular is submited.

        Args:
            inputSequenceForm (inputSequenceForm): response of th formular

        Returns:
            dict: elements from the dict
        """
        #print("\t--save inputSequence")

        InputFinder.objects.all().delete()
        Sequence.objects.all().delete()

        self.outBlast([])

        inputSequenceForm.save()
        inputSequence = inputSequenceForm.cleaned_data["inputSequence"]
        #print(inputSequence)  ###

        # run Blast
        queryFile = query_to_file(inputSequence)
        sleep(1)
        blastn = BlastIt(queryFile, dated=False)
        sleep(1)
        if blastn[0]: 
            #print(f"\n\t->parseOutBlastXml({blastn[1]})")
            self.outBlast( parseOutBlastXml(blastn[1]) )

            outfileProt = open(path.join(settings.MEDIA_ROOT, 'OceanFinder', 'outfile.prot.fasta'),'w')
            outfileNucl = open(path.join(settings.MEDIA_ROOT, 'OceanFinder', 'outfile.nucl.fasta'),'w')
            for ref in self.outBlast():
                inputName = str(InputFinder.objects.all()[0].inputSequence)
                inputName = inputName.split()[0][1:]
                outfileProt.write(f">{inputName}_{ref['name']}\n")
                outfileNucl.write(f">{inputName}_{ref['name']}\n")
                my_inputSequence = str(ref['hsp_qseq'])
                if search("TTTAAA[C-]CGGG", my_inputSequence[:len(my_inputSequence)//3]):
                    j = my_inputSequence[:len(my_inputSequence)//3].find('A-C') +1
                    inputSequence_corrected = my_inputSequence[:j] + 'A' + my_inputSequence[j+1:]
                    my_inputseq_translate = my_translate(inputSequence_corrected)
                else:
                    my_inputseq_translate = my_translate(my_inputSequence)
                outfileProt.write(''.join(cutToString(my_inputseq_translate)))
                outfileNucl.write(''.join(cutToString(my_inputSequence)))

            #for hit in self.outBlast():
                #print(f"\t\t-accession: {hit['accession']}\t-score: {hit['score']}")


    def pickBlastRef(self, pickBlastRefForm, **kwargs):
        #print('\n->POST pickBlastRef')  ###

        # pick Refseq
        blastRef = pickBlastRefForm.split()
        # BlastRef : {hit['accession']} {hit['query_start']} {hit['query_end']} {hit['sbjct_start']} {hit['sbjct_end']}
        #print(f"\t*blastRef: {blastRef}")

        my_refseq = searchRefseq_by_accession(blastRef[0]) #accession 
        ### Caution except my_refSeq = False => search found nothing ???
        # my_refseq = {'name':name, 'accession':i,'header':record.id[1:], 'sequence':record.seq}
        for Hit in self.outBlast():
            if int(Hit['accession']) == int(my_refseq['accession']):
                inputSequence = Hit['hsp_qseq']
                my_refSeq_sequence = Hit['hsp_hseq']
                break

        # refSeq
        my_refSeq_name = my_refseq['name'] +':'+ my_refseq['header'].split(':')[1]

        # inputSequence
        inputName = InputFinder.objects.all()[0].inputSequence
        inputName = inputName.split()[0][1:]

        # check length ?
        length_original = findall(":(\d+)_", my_refseq['header'])[0]
        length_outBlast = len(my_refSeq_sequence)
        if length_original != length_outBlast:
            resMuscle = complete(accNumber=int(my_refseq['accession']))
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
        with open(path.join(settings.MEDIA_ROOT, 'OceanFinder', 'outfile.aligned.fasta'),'w') as handle:
            handle.write(f">{my_refSeq_name}_nucl\n")
            handle.write(''.join(cutToString(my_refSeq_sequence))) 
            handle.write(f">{my_refSeq_name}_prot\n")
            handle.write(''.join(cutToString(my_refSeq_translate))) 
            handle.write(f">{inputName}_nucl\n")
            handle.write(''.join(cutToString(inputSequence))) 
            handle.write(f">{inputName}_prot\n")
            handle.write(''.join(cutToString(my_inputseq_translate))) 

        # InputFinder.objects.all().delete()
        # preparing alignemnt
        Sequence.objects.all().delete()
        Sequence(used_name=my_refSeq_name, isRefSeq=True,
                prot_seq=str(my_refSeq_translate), cds_seq=my_refSeq_sequence).save()

        Sequence(used_name=str(inputName), prot_seq=str(my_inputseq_translate), cds_seq=inputSequence).save()


