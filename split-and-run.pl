#!/usr/bin/env perl

# Takes a fasta file as input and splits each sequence into a separate file numbered
# sequentially. The numbered files are then submitted to a cluster using the qsub
# command

use warnings;
use File::Copy;
use Cwd;
use File::Basename;

#Splitting code from: http://archive.sysbio.harvard.edu/csb/resources/computational/scriptome/UNIX/Tools/Change.html#split_big_fasta_file_into_smaller_files__change_split_fasta_
$split_seqs=1;
$out_template="NUMBER.fasta";
$count=0;
$filenum=0;
$len=0;
while (<>) {
    s/\r?\n//;
    if (/^>/) {
	if ($count % $split_seqs == 0) {
	    $filenum++;
	    $filename = $out_template;
	    $filename =~ s/NUMBER/$filenum/g;
	    if ($filenum > 1) {
		close SHORT
	    }
	    open (SHORT, ">$filename") or die $!;
	    
	}
	$count++;
	
    }
    else {
	$len += length($_)
    }
    print SHORT "$_\n";
}
close(SHORT);
warn "\nSplit $count FASTA records in $. lines, with total sequence length $len\nCreated $filenum files like $filename\n\n";

#Submit each sequence
for ($rep=1; $rep<=$count; $rep++){
	warn "\nStarting job $rep\n";
	mkdir $rep, 0755 or die "can't create folder $rep: $!";
	move("$rep.fasta","$rep") or die "Cannot copy $rep.fasta to $rep: $!";
	system("qsub SAP-batch.job $rep");
}

