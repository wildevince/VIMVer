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

from random import choice
from string import ascii_letters, digits


from Bio.Seq import translate



def retroTranslate(protein, cds):
    """
    detect all gaps in the aligned protein
    apply them to the raw cds sequence
    return the aligned cds sequence
    """
    i = 0
    posTab = []
    for residu in protein:
        if residu == '-' or residu == '.':
            posTab.append(i)
        elif residu.strip():
            i += 1
    # cds
    out_seq = ""
    i, j = 0, 0
    for residu in cds:
        if len(posTab):
            while(i == posTab[0]):
                out_seq += '---'
                posTab = posTab[1:]
                if len(posTab) <= 0:
                    break
        if residu.split():
            j += 1
            if not (j % 3):
                i += 1
                j = 0
            out_seq += residu
    if out_seq[-3:] in ["TAA", "TAG", "TGA"]:
        out_seq = out_seq[:-3]
    return out_seq


def re_align(prt_aln, cds_raw):
    """
    re-align the protein with the traducted cds sequence
    return the corresponding cds subsequence
    """
    #
    prt_aln = ''.join(prt_aln.split())
    try:
        prt_aln = prt_aln.decode('ASCII')
    except:
        pass
    prt_seq = ''.join(prt_aln.split())
    prt_seq = ''.join(prt_seq.split('-'))
    prt_seq = ''.join(prt_seq.split('.'))
    #
    cds_raw = ''.join(cds_raw.split())
    try:
        cds_raw = cds_raw.decode('ASCII')
    except:
        pass
    cds_seq = ''.join(cds_raw.split())
    cds_seq = ''.join(cds_seq.split('-'))
    cds_seq = ''.join(cds_seq.split('.'))
    #
    translation = translate(cds_seq)
    ########################################
    i = translation.find(prt_seq)
    cds_seq = cds_seq[i*3:3*(i+len(prt_seq))]
    ##########################################
    return retroTranslate(prt_aln, cds_seq)


def isHeader(line):
    """
    return true if 'line' is a fasta header
    by comparing the first character with '>' and '#'
    """
    starters = ['>', '#', ':']
    if line[0] in starters:
        return True


def isNucl(line):
    """
    return true if 'line' is a nucleotidic sequence
    by returning False if meet something else than 'A', 'G', 'C', 'T', 'U'.
    """
    nucl = ['A', 'G', 'C', 'T', 'U']
    try:
        line = line.decode('ASCII')
    except:
        pass
    line = ''.join(line.split())
    line = ''.join(line.split('-'))
    line = ''.join(line.split('.'))
    for res in line:
        if res.strip().upper() not in nucl:
            return False
    return True


def generate3rdline(refseq:str, inputseq:str, nucl=False):
    matchseq = ''
    refseq_length = range(len(refseq))
    for k in refseq_length:
        if 'X' in [inputseq[k], refseq[k]] or (nucl and 'N' in [inputseq[k], refseq[k]]):
            matchseq += '~'
        elif refseq[k] == inputseq[k]:
            matchseq += ' '
        else :
            matchseq += '*'
    return matchseq


def giveMe_seqArray(refseq:str, inputseq:str, match:str, step:int):
    def numberOfSubTable(sequence:str, step:int):
        N = range(len(sequence)//step +(1 if(len(sequence)%step != 0) else 0))
        return N
    def cutSequence(sequence:str, step:int):
        res = []
        N = len(numberOfSubTable(sequence, step))
        while len(res) < N:
            if len(sequence) > step:
                res.append(sequence[:step])
                sequence = sequence[step:]
            else:
                res.append(sequence)
        return res
    
    def giveMe_lineNumbers(sequence:str, step:int):
        N = numberOfSubTable(sequence, step)
        start = [n*step for n in N]
        end = [(n+1)*step for n in N]
        end[-1] = len(sequence)

        res = [(start[k],end[k]) for k in N]

        return res
    
    numbers  = giveMe_lineNumbers(refseq, step)
    refseq   = cutSequence(refseq, step)
    inputseq = cutSequence(inputseq, step)
    match    = cutSequence(match, step)

    i = range(len(refseq))
    res = [{
        'refseq':refseq[k],
        'inputseq':inputseq[k],
        'match':match[k]+'_',
        'number_start':numbers[k][0]+1,
        'number_end':numbers[k][1]
    } for k in i]

    return res


def cutToString(text:str, nbr=120):
    result = ""
    while len(text) > nbr:
        result += (text[:120] +'\n')
        text = text[120:]
    result += (text +'\n')
    return result


def generate_key():
    return ''.join(choice(ascii_letters + digits) for _ in range(6))