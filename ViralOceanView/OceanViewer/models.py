from django.db import models
from django.core.files.storage import FileSystemStorage

from OceanFinder.models import Job


# Create your models here.

fs = FileSystemStorage(location='/OceanViewer/files')


class Sequence(models.Model):
    """
    Model
    ## Attributs
    genbank accession number, used name,
    protein and cds sequences
    """
    job = models.ForeignKey(to=Job, on_delete=models.CASCADE)  #FK Job

    accNbr_gb = models.CharField(
        verbose_name="genbank accession number",
        max_length=12,
        null=True,
        blank=True)
    used_name = models.CharField(default="example_1", max_length=45)
    isRefSeq = models.BooleanField(default=False)
    prot_seq = models.TextField(
        default="MGG-G", verbose_name="Aligned protein sequence")
    cds_seq = models.TextField(
        verbose_name="CDS",
        blank=True)

    class Meta:
        ordering = ['used_name']

    def __str__(self):
        return self.used_name

    def __repr__(self):
        return self.used_name

    def getSeq(self, key):
        if key == 'prot_seq':
            return self.prot_seq
        elif key == 'cds_seq':
            return self.cds_seq
        else:
            return self.__repr__()

