from datetime import datetime
from django.db import models


# Create your models here.

class Job(models.Model):
    #id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    key = models.CharField(unique=True, max_length=6, verbose_name='KEY')
    date = models.DateTimeField(auto_now_add=True)
    queryFasta = models.FilePathField()
    outBlastXML = models.FilePathField()

    #@classmethod
    #def auto_clean():
    #    date_laps = 24 #hours
    #    d, H = datetime.now().strftime('%d %H').split()
        
    class Meta:
        ordering = ['date']


class Input(models.Model):
    sequence = models.TextField(
        verbose_name="input fasta sequence",
        default= ">input seq test\nATGGGG---",
        blank=False)
    header = models.CharField(max_length=50)
    name = models.CharField(max_length=25)
    job = models.CharField(max_length=6)  #FK Job

    class Meta:
        ordering = ['name']


class OutBlast(models.Model):
    job = models.CharField(max_length=6)  #FK Job
    name = models.CharField(max_length=25)
    definition = models.CharField(max_length=50)
    accession = models.SmallIntegerField()
    identity = models.SmallIntegerField()
    score = models.SmallIntegerField()
    sbjct_lenght = models.IntegerField()

    hsp_hseq = models.TextField()  # my_refSeq_sequence
    sbjct_start = models.IntegerField()
    sbjct_end = models.IntegerField()
    hseq_transl = models.TextField()  # my_refSeq_translate

    hsp_qseq = models.TextField()  # inputSequence
    query_start = models.IntegerField()
    query_end = models.IntegerField()
    qseq_transl = models.TextField()  # my_inputseq_translate

    class Meta:
        ordering = ['name']



