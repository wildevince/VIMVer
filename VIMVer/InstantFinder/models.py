from django.db import models
from django.db.models.fields.files import FileField


# Create your models here.
class InputFinder(models.Model):
    """
    Model:
        genomic input sequence

    Attributs:
        inputSequence (str): fasta sequence
    """ 
    inputSequence = models.TextField(
        verbose_name="input fasta sequence",
        default= ">input seq test\nATGGGG---",

        blank=False)



class BlastRef:
    outBlastList = []



class outBlastXML(models.Model):
    file = FileField()

