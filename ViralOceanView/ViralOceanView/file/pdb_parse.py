#!/usr/bin/env python3


from os import getcwd
from os.path import dirname, join
from Bio import SeqIO


DB = join(getcwd(), 'dataBase_local')
DB_pdb = join(DB, 'PDB')
ProtPath = join(DB, 'localDataBase_prot.fasta')
NuclPath = join(DB, 'localDataBase_nucl.fasta')

res:dict={}



