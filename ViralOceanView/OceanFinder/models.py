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

from django.db import models

from .tests import DefaultFastaSeq



class Job(models.Model):
    """ Model: temporarily keep information for each request jobs with-in 24h-ish """
    key = models.CharField(primary_key=True, max_length=6)  #PK
    date = models.CharField(max_length=5, null=True)
    queryFasta = models.FilePathField(null=True)
    outBlastXML = models.FilePathField(null=True)

    class Meta:
        ordering = ['date']


class Input(models.Model):
    """ Model: corresponding to the user's input in fasta format [foreign key -> job] """
    job = models.ForeignKey(to=Job, on_delete=models.CASCADE)  #FK Job

    sequence = models.TextField(
        verbose_name="input nucl fasta sequence",
        default=DefaultFastaSeq,
        blank=False)
    header = models.TextField()
    name = models.CharField(max_length=25)


class OutBlast(models.Model):
    """ Model: parsing Blast result after [foreign key -> job] """
    job = models.ForeignKey(to=Job, on_delete=models.CASCADE)  #FK Job
    
    name = models.CharField(max_length=25)
    definition = models.TextField()
    accession = models.SmallIntegerField()

    identity = models.SmallIntegerField()
    score = models.SmallIntegerField()
    sbjct_length = models.IntegerField()

    hsp_hseq = models.TextField()  # my_refSeq_sequence
    sbjct_start = models.IntegerField()
    sbjct_end = models.IntegerField()
    hseq_transl = models.TextField()  # my_refSeq_translate

    hsp_qseq = models.TextField()  # inputSequence
    query_start = models.IntegerField()
    query_end = models.IntegerField()
    qseq_transl = models.TextField()  # my_inputseq_translate

