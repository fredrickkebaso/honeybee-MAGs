#!/usr/bin/env python3
import sys
import os
import argparse
import glob
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

"""
This script reads the ffn file made by prodigal and makes a new one where the name of the contig
starts with sample name prefixed with '_' as a separator and only keeps orfs that are marked have 
a flag of 00 and are more than 300 bp long.
The corresponding faa records can be parsed out of the file in 06_metagenomicORFs/{sample}/{sample}.faa
The corresponding gff records can be parsed out of the file in 06_metagenomicORFs/{sample}/{sample}.faa
or can be written by parsing the ffn file using biopython (https://biopython.org/wiki/GFF_Parsing).
"""

# Usage: python3 scripts/filt_orfs.py --ffn_in data/ffn/contigs.ffn --ffn_out data/ffn/contigs_filt.ffn --sample sample --log data/ffn/contigs_filt.log

parser = argparse.ArgumentParser()
requiredNamed = parser.add_argument_group('required arguments')
requiredNamed.add_argument('--ffn_in', metavar="ffn_in", required=True, help="provided ffn input", action="store")
requiredNamed.add_argument('--ffn_out',metavar="ffn_out",required=True, help="filtered ffn output", action="store")
requiredNamed.add_argument('--sample',metavar="ffn_out",required=True, help="filtered ffn output", action="store")
requiredNamed.add_argument('--log',metavar="ffn_out",required=True, help="filtered ffn output", action="store")

args = parser.parse_args()
ffn_in = args.ffn_in
ffn_out = args.ffn_out
sample = args.sample
log = args.log

count_records = 0
count_records_filt = 0

seq_records_filt = []

for seq_record in SeqIO.parse(ffn_in, "fasta"):
    count_records += 1
    header = seq_record.id
    # print(header)
    length = len(seq_record)
    # print(length)
    partial_flag = seq_record.description.split(";")[1].split("=")[1]
    # print(partial_flag)
    new_header = sample+"_"+header
    if length > 300 and partial_flag == "00":
        count_records_filt += 1
        seq_record.id = new_header
        seq_record.description = ''
        seq_records_filt.append(seq_record)

SeqIO.write(seq_records_filt, ffn_out, "fasta")

with open(log, "w") as log_fh:
    log_fh.write(f"sample\tcount_records\tcount_records_filt\tfraction\n")
    fraction = count_records_filt/count_records*100
    log_fh.write(f"{sample}\t{count_records}\t{count_records_filt}\t{fraction}\n")
