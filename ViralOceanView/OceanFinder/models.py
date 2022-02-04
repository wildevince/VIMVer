from pickle import TRUE
from django.db import models
from django.db.models.fields.files import FileField
from numpy import identity


# Create your models here.

class Input(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    sequence = models.CharField(
        verbose_name="input fasta sequence",
        default= ">input seq test\nATGGGG---",
        blank=False)
    header = models.CharField()
    name = models.CharField()



class Job(models.Model):
    key = models.CharField(primary_key=True, max_length=6)
    query = models.ForeignKey(to=Input, on_delete=models.CASCADE)  ####################################### FK
    date = models.DateTimeField()
    queryFasta = models.FilePathField()
    outBlastXML = models.FilePathField()
    outBlast = models.CharField() ######## FK


class OutBlast(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    job = models.ForeignKey(to=Job, on_delete=None)
    name = models.CharField()
    definition = models.CharField()
    accession = models.SmallIntegerField()
    identity = models.SmallIntegerField()
    score = models.SmallIntegerField()
    sbjct_lenght = models.IntegerField()
    hsp_hseq = models.CharField()
    sbjct_start = models.IntegerField()
    sbjct_end = models.IntegerField()
    hsp_qseq = models.CharField()
    query_start = models.IntegerField()
    query_end = models.IntegerField()
    qseq_transl = models.CharField()

