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
from django.core.files.storage import FileSystemStorage

from OceanFinder.models import Job


# Create your models here.

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

