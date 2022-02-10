from django.db import models


# Create your models here.

class Job(models.Model):
    #id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    key = models.CharField(primary_key=True, max_length=6)  #PK
    date = models.CharField(max_length=5, null=True)
    #date = models.DateTimeField(auto_now_add=True)
    queryFasta = models.FilePathField(null=True)
    outBlastXML = models.FilePathField(null=True)

    class Meta:
        ordering = ['date']


class Input(models.Model):
    #id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    job = models.ForeignKey(to=Job, on_delete=models.CASCADE)  #FK Job
    #job = models.CharField(max_length=6)  #FK Job

    sequence = models.TextField(
        verbose_name="input fasta sequence",
        default= ">input seq test\nATGGGG---",
        blank=False)
    header = models.TextField()
    name = models.CharField(max_length=25)


class OutBlast(models.Model):
    #id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    job = models.ForeignKey(to=Job, on_delete=models.CASCADE)  #FK Job
    #job = models.CharField(max_length=6)  #FK Job
    
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

