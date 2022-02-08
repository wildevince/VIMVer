from datetime import datetime
from pickle import TRUE
from django.db import models


# Create your models here.

class Job(models.Model):
    key = models.CharField(primary_key=True, max_length=6)
    date = models.DateTimeField(default=datetime.now)
    queryFasta = models.FilePathField()
    outBlastXML = models.FilePathField()
    #outBlast = models.CharField() ######## FK


class Input(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    sequence = models.TextField(
        verbose_name="input fasta sequence",
        default= ">input seq test\nATGGGG---",
        blank=False)
    header = models.CharField(max_length=50)
    name = models.CharField(max_length=25)
    job = models.ForeignKey(to=Job, on_delete=models.CASCADE)


class OutBlast(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    job = models.ForeignKey(to=Job, on_delete=models.CASCADE)
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

