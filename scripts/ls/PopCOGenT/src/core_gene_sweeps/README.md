# Purpose
Finds core genome sweep regions by identifying low diversity, monophyletic (within a population) regions in a whole-genome alignment. 

# Important caveats

* This module is only designed to detect sweeps that differentiate the most closely related populations, i.e., populations that are still connected by some gene flow. This corresponds to populations that share the same `Main_cluster` designation from PopCOGenT but different `sub_cluster` assignments. For example, this can detect sweeps that differentiate population `0.0` from population `0.1` but not sweeps differentiating population `0.0` from population `1.0`. 

* Because this module requires the creation of a whole genome alignment and the generation of thousands of phylogenies, we have only been successful at using it for examining groups of less than 100 genomes. That is, the `Main_cluster` examined should not have more than 100 members.

# Setup

Requires a `*.cluster.tab.txt` file generated by PopCOGenT and the associated `.fasta` genome files. Also requires specifying a `focus_population`, i.e., one of the populations in the `Cluster_ID` column of the `*.cluster.tab.txt` file. The file should be filtered to only include the strains belonging to a single `Main_cluster` of interest and the input folder of genome files should likewise only contain the genomes belonging to the `Main_cluster` of interest. A future version will automatically deal with this so that inputs will not have to be modified.

# Parameters

## Input file specifications
* `project_dir`: absolute path to a directory for output files
* `input_contig_dir`: absolute path to directory containing genomes for 
input_contig_dir = /nobackup1b/users/davevan/pop_genomes/serial_phybreak/contigs/
contig_dir = /nobackup1b/users/davevan/pop_genomes/serial_phybreak/genome/
* `input_contig_extension`: 
* `pop_infile_name`: path to file with populations calls from PopCOGenT
* `output_prefix`: prefix to identify output files
* `focus_population`: specific population identifier from the PopCOGenT population calls that you want to investigate
* `ref_iso`: identifier (filename without the extension) for reference genome to use for alignments. file must contain only one contig, either because it is closed or by stitching together contigs with Ns.
* `ref_contig`: sequence ID (i.e., first word in the fasta file header) of the reference genome

## Parameters for alignment block processing
* `len_block_threshold`: minimum length of degapped alignment block
* `gap_prop_thresh`: maximum proportion of alignment block that can contain gaps
* `window_size`: number of SNPs to include per tree
* `window_overlap`: number of SNPs to overlap between windows - larger overlaps will decrease number of trees generated
* `percentile_threshold`: within population diversity percentile cutoff
* `min_physplit_window_size`: minimum number of SNPs in a row that satisfy the monophyly and percentile threshold to warrant creating a new range to output

## Utility options/paths
* `MUGSY_source`: Command to activate mugsy environment file.
* `phyML_loc`: Path to run phyML
* `phyML_properties`: parameters for phyML

# Output
* `align/*.core.fasta`: The concatenated core genome alignment of all genomes
* `*.core_sweeps.csv`: The positions (in the coordinates of the whole genome alignment) of core genome sweeps.
* `Start`: Start position indexed at 0.
* `End`: End position indexed at 0.
* `Start tree`: Tree identifier that indicates the 100 SNP window where the region starts.
* `End tree`: Tree identifier that indicates the 100 SNP window where the region ends.
* `pop_pi`: Within-population nucleotide diversity in the sweep region
* `Length`: Length of sweep region
* `Midpoint`: Midpoint of sweep region in the coordinates of the multiple genome alignment.
* `ci_low` and `ci_high`: 95% confidence interval for nucleotide diversity given average genome-wide nucleotide diversity within the population.

# Usage

Set all relevant parameters in `phybreak_parameters.txt`. Load PopCOGenT environment with `source activate PopCOGenT`. Run scripts in sequence from 1-7 (i.e., `python {script_name}`). For each population for which you wish to find sweeps, change the `focus_population` parameter and re-run scripts 3-7.