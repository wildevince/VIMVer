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

#!/usr/bin/env python3

from math import trunc
from multiprocessing.connection import wait
from os import path, getcwd, listdir
from re import findall
from time import sleep
from datetime import datetime
import subprocess

from Bio import SeqIO
from Bio.Blast.Applications import NcbiblastnCommandline
from Bio.Blast.Applications import NcbiblastpCommandline
from Bio.Blast.Applications import NcbimakeblastdbCommandline
from Bio.Align.Applications import MuscleCommandline
from Bio.Blast import NCBIXML, Record

from django.conf import settings

from OceanFinder.scr.OceanFinder import searchRefseq_by_accession



def doBashline(cline, log=False, args=None):
    """Allows to excecute Bash command.

    Args:
        cline (str): the bash command
        log (bool, optional): if True then print the command in the console. Defaults to False.
        args (any, optional): Why not ? Defaults to None.
    """
    if log:
        print(cline)
    cline = str(cline).split(' ')
    subprocess.Popen(cline)


def CreateDataBase(testpath=False):
    """Generates 'nucl' and 'prot' dataBase from those two files : 
        'localDataBase_nucl.fasta' and 
        'localDataBase_prot.fasta.
        Must be excecuted before the fist Blast, otherwise it wouldn't work proprely.
    """
    if testpath:
        localDB_nucl = path.join(testpath, "localDataBase_nucl.fasta")
        localDB_prot = path.join(testpath, "localDataBase_prot.fasta")
    else:
        localDB_nucl = path.join(settings.DATABASE, "localDataBase_nucl.fasta")
        localDB_prot = path.join(settings.DATABASE, "localDataBase_prot.fasta")
    doBashline(NcbimakeblastdbCommandline(
        dbtype='nucl', input_file=localDB_nucl))
    doBashline(NcbimakeblastdbCommandline(
        dbtype='prot', input_file=localDB_prot))


def CheckDataBaseIntegrity():
    """Check for the integrity of the local dataBases ( "localDataBase_nucl.fasta" and "localDataBase_prot.fasta")
    Prints and counts the sequences. 
    
    Usage: 
        purely indicative
    """
    created = False
    Fasta = {}
    log = open(path.join(settings.MEDIA_ROOT, 'OceanFinder','log.txt'), 'w')
    Files = ("localDataBase_nucl.fasta", "localDataBase_prot.fasta")

    for filename in listdir(settings.DATABASE):
        #print(filename)
        if filename in Files:
            with open(path.join(settings.DATABASE, filename), 'r') as fileHandler:
                # foreach fasta sequence in the file
                for record in SeqIO.parse(fileHandler, 'fasta'):
                    # find protRef
                    reResult = findall("\[([^\[]+)\]", str(record.id))
                    if ':' in reResult[0]:
                        protRef = reResult[0].split(':')[-1]
                    else:
                        protRef = reResult[0]
                    # check for residu_type
                    if 'nucl' in record.id[-6:]:
                        k = 'nucl'
                    elif 'prot' in record.id[-6:]:
                        k = 'prot'
                    # into dict
                    if not protRef in Fasta:
                        Fasta[protRef] = {'nucl': 0, 'prot': 0}
                    Fasta[protRef][k] += 1
                # end parse
            # end handler
        elif not (filename in ["__init__.py"]):
            if not created:
                created = True
    # end dir parse
    if not created:
        CreateDataBase()
    log.close()
    # check FASTA
    for protRef, counts in Fasta.items():
        output = f">{counts['nucl']}nucl{'*' if counts['nucl']>1 else ''}\t"
        output += f"{counts['prot']}prot{'*' if counts['prot']>1 else ''}\t"
        output += f"{protRef}"
        #print(output)


def query_to_file(query:str, jobKey:str):
    """create a file in "file/OceanFinder/"

    Args:
        query (str): fasta sequence

    Returns:
        (str): path to file
    """
    filepath = path.join(settings.MEDIA_ROOT,'OceanFinder','out', jobKey+"_query.fasta")
    with open(filepath, 'w') as handle:
        handle.write(query)
    return filepath


def BlastIt(query, jobKey:str, dbType='nucl', **kwargs):
    """Controls arguments before Blast the querry using bash command.

    Args:
        query (str): in file's name.
        dbType (str, optional): type of the local database ('nucl' or 'prot'). Defaults to 'nucl'.
        outXML (str, optional): out file's name. Defaults to 'outBlast.xml'.

    Returns:
        bash command: 
            blast{n or p} -q {path to query} -db {path to dataBase} -o {path to outXML}
    """
    # argument control : query
    queryPath = path.join(settings.MEDIA_ROOT,'OceanFinder','out',query)
    if not path.exists(queryPath):
        return (False, "Query file doesn't exist")

    # argument control : db
    if dbType == 'nucl':
        dbPath = path.join(settings.DATABASE, "localDataBase_nucl.fasta")
    elif dbType == 'prot':
        dbPath = path.join(settings.DATABASE, "localDataBase_prot.fasta")
    else:
        return (False, "plz choose : 'nucl' or 'prot'")

    # argument control : outXML
    outXMLPath = path.join(settings.MEDIA_ROOT,'OceanFinder','out', jobKey+'_outBlast.xml')
    #print(outXMLPath)

    # argument control : kwargs (more arguments ?)
    if not 'log' in kwargs:
        log = True

    if dbType == 'nucl':
        doBashline(NcbiblastnCommandline(
            cmd="blastn", query=queryPath, outfmt=5, out=outXMLPath, db=dbPath), False)
        sleep(1)
        return (True, path.basename(outXMLPath))
    elif dbType == 'prot':
        doBashline(NcbiblastpCommandline(
            cmd="blastp", query=queryPath, outfmt=5, out=outXMLPath, db=dbPath), False)
        sleep(1)
        return (True, path.basename(outXMLPath))
    return (False,path.basename(outXMLPath))


def complete(accNumber:int, jobKey:str):
        """call Muscle to realign proprely.

        Args:
            accNumber (str): accession number in local database

        Returns:
            [dict]: ['name', 'identity', 'sbjct_lenght', 'score', 'definition', 'accession',
                    'hsp_qseq', 'hsp_hseq', 'query_start', 'query_end', 'sbjct_start', 'sbjct_end']
        """
        queryPath = path.join(settings.MEDIA_ROOT,'OceanFinder','out', jobKey+'_query.fasta')
        outPath = path.join(settings.MEDIA_ROOT,'OceanFinder','out', f"{jobKey}_out{accNumber}_muscle.fasta")
        inPath = path.join(settings.MEDIA_ROOT,'OceanFinder','out', f"{jobKey}_in{accNumber}_muscle.fasta")

        with open(queryPath) as handle:
            for record in SeqIO.parse(handle, 'fasta'):
                query = {'sequence':record.seq, 'header':record.id}
        refseq = searchRefseq_by_accession(accNumber)

        with open(inPath, 'w') as handle:
            handle.write(f">{'query'}\n")
            handle.write(f"{query['sequence']}\n")
            handle.write(f">{'refseq'}\n")
            handle.write(f"{refseq['sequence']}\n")
        
        doBashline(MuscleCommandline('muscle', input=inPath, out=outPath))
        sleep(2)

        wait_turn = 0
        while (not path.exists(outPath)) and wait_turn<10:
            wait_turn += 1
            print(f"waiting for muscle: {wait_turn} seconds ")
            sleep(1)
        if not path.exists(outPath):
            return False
                
        with open(outPath) as handle:
            for record in SeqIO.parse(handle, 'fasta'):
                if record.id == 'query':
                    query['aligned'] = record.seq
                else :
                    refseq['aligned'] = record.seq
        
        res = {'name':refseq['name'], 'score':'???', 'accession':accNumber, 'definition':refseq['header']}
        #
        sbjct_length = int(findall("\d:([\d]+)_\[", refseq['header'])[0])
        identity, started, gaps = (0, False, [0])
        for i, residu in enumerate(refseq['aligned']):
            if residu == '-':
                if started :
                    gaps.append(0)
                else:
                    gaps[-1] += 1 
                started = False
            else: 
                started = True
                if residu == query['aligned'][i]:
                    identity += 1
        
        res['sbjct_length'] = sbjct_length
        res['query_start'] = gaps[0] +1
        res['query_end'] = len(query['aligned']) -gaps[-1]
        res['sbjct_start'] = 1
        res['sbjct_end'] = sbjct_length
        res['identity'] = identity
        res['hsp_qseq'] = query['aligned'][res['query_start']-1: res['query_end']-1]
        res['hsp_hseq'] = refseq['aligned'][res['query_start']-1: res['query_end']-1]

        return res 


def parseOutBlastXml(jobkey):

    def extractHeader(line):
        res = findall("\[(.+)\]", line)[0]
        if ':' in res:
            res = res.split(':')[1]
        return str(res)

    DataOut = path.join(settings.MEDIA_ROOT,'OceanFinder','out')
    
    #outBlastFile = outBlastXML.objects.all()[0].file
    outBlastFile = path.join(DataOut, jobkey+'_outBlast.xml')
    #print(outBlastFile)
    wait_turn = 0
    while (not path.exists(outBlastFile)) and wait_turn<10:
        wait_turn += 1
        print(f"waited {wait_turn} seconds")
        sleep(1)
    if not path.exists(outBlastFile):
        return False
    
    outBlastDict = {}
    
    with open(outBlastFile) as handler:
        for record in NCBIXML.parse(handler):  # iter
            for alignment in iter(record.alignments):
                accNumber = alignment.accession
                length = alignment.length
                for hsp in iter(alignment.hsps):
                    pickme = False
                    if accNumber in outBlastDict:
                        if not outBlastDict[accNumber]['score'] == '???':
                            outBlastDict[accNumber] = complete(int(accNumber), jobkey)
                    else:
                        #identity = f"{float(hsp.identities)/float(length)*100}%"
                        identity = hsp.identities
                        score = hsp.score
                        header = extractHeader(alignment.hit_def)
                        outBlastDict[accNumber] = {
                            'name': header, 'identity': identity, 'sbjct_length':length, 
                            'score':score, 'definition':alignment.hit_def, 'accession':accNumber,
                            'hsp_qseq':hsp.query, 'hsp_hseq':hsp.sbjct, 
                            'query_start':hsp.query_start, 'query_end':hsp.query_end,  
                            'sbjct_start': hsp.sbjct_start, 'sbjct_end':hsp.sbjct_end
                            }
                        #print(f"\t\t\t-{accNumber}: ({header}, {score}, {hsp.query[:6]}, {hsp.sbjct[:6]}, ...)")
    return [hit for key, hit in outBlastDict.items()]

