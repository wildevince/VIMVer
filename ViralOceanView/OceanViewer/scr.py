#!/usr/bin/env python3
from re import S, findall
from os import path

from Bio import Entrez, SeqIO
from Bio.Seq import translate

from django.conf import settings



def get_nucl_accNbr(accNbr):
    """
    input: accession number

    little recursivity (if necessary)

    return: the nucleotide accession number
    """
    Entrez.email = "oceanViewer@example.com"
    try:
        with Entrez.efetch(
            db='nucleotide', rettype='gb', temode='text', id=accNbr
        ) as handle:
            seq_record = SeqIO.read(handle, 'gb')
        return seq_record.id
    except:
        try:
            with Entrez.efetch(
                db='protein', rettype='gb', temode='text', id=accNbr
            ) as handle:
                seq_record = SeqIO.read(handle, 'gb')
                for feat in seq_record.features:
                    if feat.type == "CDS":
                        accNbr = ''.join(feat.qualifiers['coded_by']).split(':')[0]
                        return accNbr
        except:
            return None


def get_CDS(accNbr, out_CDS={}):
    """Extract the CDS from a ncbi request

    Args:
        accNbr (str): accession number.

    Returns:
        (dict): {'header':(str), 'sequence':(str)}  
    """
    Entrez.email = "OceanViewer@example.com"
    try:
        with Entrez.efetch(
            db='nucleotide', rettype='gb', temode='text', id=accNbr
        ) as handle:
            seq_record = SeqIO.read(handle, 'gb')
        seqId = seq_record.id
        for feat in seq_record.features:
            if feat.type == "CDS":
                result = findall("([\d]+(:|..)[\d]+)", str(feat.location))
                for thing in result:
                    thing = thing[0].split(thing[1])
                    start = int(thing[0])
                    end = int(thing[1])
                    out_CDS[seqId] = {'header': "", 'sequence': ""}
                    out_CDS[seqId]["header"] = f"{seqId}:cds:{start}..{end}:"
                    line = str(seq_record.seq)[start:end]
                    while(len(line) > 120):
                        out_CDS[seqId]["sequence"] += (line[0:120]+'\n')
                        line = line[120:]
                    out_CDS[seqId]["sequence"] += (line+'\n')
    except:
        try:
            with Entrez.efetch(
                db='protein', rettype='gb', temode='text', id=accNbr
            ) as handle:
                seq_record = SeqIO.read(handle, 'gb')
                for feat in seq_record.features:
                    if feat.type == "CDS":
                        accNbr = ''.join(feat.qualifiers['coded_by']).split(':')[0]
                        return get_CDS(str(accNbr), out_CDS)
        except:
            return None
    return out_CDS[accNbr]


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