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


import os
import re

from django.conf import settings 

from Bio import Entrez, SeqIO, Seq


### querry sequence
def searchingRefSeq(
                    residu_type = 'nucleotide',
                    IDs = ['NC_045512.2'], 
                    outFasta = {},
                    log=False,
                    k=0):
    """Get and Read the genbank file of 'NC_045512.2' in ncbi refSeq dataBase. 

    Args:
        residu_type (str, optional): 'nucleotide' or 'protein'. Defaults to 'nucleotide'.
        IDs (list, optional): Defaults to 'NC_045512.2'.
        outFasta (dict, optional): returned dict used in recursive. Defaults to empty.

    Returns:
        dict: (header : sequence)
    """
    ## sub-functions
    def findInFeatQualifiers(featQualifiers, keys=('gene', 'product', 'protein_id')):
        """ Return information from feat.qualifiers (featQualifiers) in a tuple
        """
        def find_key(key, qualifiers):
            """ Return specific information (key) from feat.qualifiers (featQualifiers) 
            """
            if key in qualifiers:
                return str('_'.join(qualifiers[key][0].split()))
            return False
        return [find_key(key, featQualifiers) for key in keys]
    
    def stringInDict(header, sequence, Dict):
        """Modify the Dict passed by reference.
        Dict[header] = sequence.

        Args:
            header (str): unique
            sequence (str): sequence passed by copy
            Dict (dict): modified dictionary
        
        Example:
        >>>
        """
        Dict[header] = ""
        while(len(sequence) > 120):
            Dict[header] += (sequence[0:120]+'\n')
            sequence = sequence[120:]
        Dict[header] += (sequence+'\n')
    
    def getBoundaries(location):
        def getStartEnd(rline):
            rline = rline[0].split(rline[1])
            return (int(rline[0]), int(rline[1]))
        res = re.findall("([\d]+(:|..)[\d]+)", str(location))
        return [getStartEnd(rline) for rline in res]

    ## initialisation
    Entrez.email = "oceanViewer@example.com"
    residu_type= str(residu_type)
    if not log :
        log = open(os.path.join(settings.MEDIA_ROOT,'OceanFinder',log.txt),'w')
        

    ## querries
    for i in IDs:
        with Entrez.efetch(
            db=residu_type, rettype='gb', temode='text', id=i
        )as handle:
            seq_record = SeqIO.read(handle, 'gb')
            accNumber = seq_record.id
            log.write(f"accession\t{accNumber}\n")  ###
        
            for feat in seq_record.features:
                
                # searching in 'nucl' refSeq
                # feat type is 'CDS'
                if (feat.type == 'CDS') and ('nucl' in residu_type):
                    orf, protRef, protID = findInFeatQualifiers(feat.qualifiers)
                    log.write(f"\t-CDS:\t{orf}, {protRef}, {protID}\n")  ###

                    if not orf == "ORF1ab":
                        
                        # get translation if is available
                        trad = str(findInFeatQualifiers(feat.qualifiers, ('translation',))[0])
                        if trad:
                            ## make header
                            header = f"{protID}:{len(trad)}_[{protRef}]_prot"
                            log.write(f"\t\t--translation\t{header}; {trad[:6]}... ok\n")  ###
                            stringInDict(header, trad, outFasta)
                        
                        # find protein boundaries
                        for start, end in iter(getBoundaries(str(feat.location))):
                            ## make header
                            header = f"{accNumber}:{start}..{end}:{end-start}_[{orf}:{protRef}]_nucl"
                            ## save in dictonary
                            sequence = str(seq_record.seq)[start:end]

                            log.write(f"\t\t-- {header}; {sequence[:6]}... ")  ###
                            if not header in outFasta :
                                log.write("ok")  ###
                                stringInDict(header, sequence, outFasta)
                            log.write("\n")  ###

                    else :
                        log.write(f"\nsearching '{protID}' ...\n")  ###
                        searchingRefSeq(IDs=[protID], residu_type='protein', outFasta=outFasta, log=log, k=k)
                        log.write(f"\n...back to {accNumber}\n")  ###
                
                # feat type is 'mat_peptide'
                if feat.type == 'mat_peptide':
                    orf, protRef, protID = findInFeatQualifiers(feat.qualifiers)
                    log.write(f"\t-mat_peptide:\t{orf}, {protRef}, {protID}\n")  ###
                    
                    # find protein boundaries
                    catseq=[]
                    for start, end in iter(getBoundaries(str(feat.location))):
                        ## sequence
                        sequence = str(seq_record.seq)[start:end]
                        ## header
                        catseq.append({'start': start, 'end': end, 'sequence': sequence})
                    start = min([ k['start'] for k in catseq ])
                    end = max([ k['end'] for k in catseq ])
                    sequence = "".join([k['sequence'] for k in catseq ])

                    if (residu_type.startswith('nucl')):
                        header = f"{accNumber}:{start}..{end}:{end-start}_[{orf}:{protRef}]_nucl"
                    else :
                        header = f"{protID}:{len(sequence)}_[{protRef}]_prot"
                    ## save in dictonary
                    log.write(f"\t\t-- {header}; {sequence[:6]}... ")  ###
                    if not header in outFasta :
                        log.write("ok")  ###
                        stringInDict(header,sequence,outFasta)
                    log.write("\n")  ###
    return outFasta


def dictToFile(outDict, testpath=False):
    """Write on 'localDataBase_nucl.fasta' and 'localDataBase_prot.fasta'
    """
    if not testpath:
        LDB_nucl = open(os.path.join(settings.DATABASE,"localDataBase_nucl.fasta"),'w')
        LDB_prot = open(os.path.join(settings.DATABASE,"localDataBase_prot.fasta"),'w')
    else:
        LDB_nucl = open(os.path.join(testpath,"localDataBase_nucl.fasta"),'w')
        LDB_prot = open(os.path.join(testpath,"localDataBase_prot.fasta"),'w')
    for record, seq in outDict.items():
        print(record)
        if record.endswith('nucl'):
        #if ( 'nucl' in record[-6:] ):
            LDB_nucl.write(f">{record}\n")
            LDB_nucl.write(seq)
        elif record.endswith('prot'):
        #elif ( 'prot' in record[-6:] ):
            LDB_prot.write(f">{record}\n")
            LDB_prot.write(seq)
        else:
            print(f"ERROR! {record}")
    LDB_nucl.close()
    LDB_prot.close()


def searchRefseq_by_name(head):
    with open(os.path.join(settings.DATABASE, 'localDataBase_nucl.fasta')) as handle:
        for record in SeqIO.parse(handle, 'fasta'):
            name = str(record.id.split('[')[1].split(']')[0])
            if (record.id).endswith(head):
                return {'name':name, 'header':head, 'sequence':record.Seq}
    return False


def searchRefseq_by_accession(accNumber):
    print(f"\n\t->searchRefseq by accession ({accNumber}) : ")
    with open(os.path.join(settings.DATABASE, 'localDataBase_nucl.fasta')) as handle:
        for i, record in enumerate(SeqIO.parse(handle, 'fasta')):
            if i == int(accNumber):
                name = str(record.id.split('[')[1].split(']')[0])
                if ':' in name:
                    name = name.split(':')[1]
                print(f"\t\t=> accession: {i}, name: {name}")
                return {'name':name, 'accession':i, 'header':record.id, 'sequence':record.seq}
    return False


def my_translate(sequence, indel=('-','.')):
    trans = ""
    codon = ''
    i = 0
    for nucl in sequence:
        if nucl in indel:
            i += 1
            if i%3 == 0:
                trans += '-'
            continue
        codon += str(nucl)
        if len(codon)%3 == 0:
            if 'N' in codon:
                trans += 'X'
            else:
                trans += str(Seq.translate(codon))
            codon = ''
    return trans


###########################################################
###########################################################

#dictToFile(searchingRefSeq(), testpath="/home/vincentwilde/Documents/ViralOceanView/ViralOceanView/ViralOceanView/file/dataBase_local/")