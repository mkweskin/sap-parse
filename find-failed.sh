#!/bin/sh

# Takes an integer as input for the number of sequentially numbered directories
# to search for the file index.html. If they are not found this is used as an
# indication that the SAP run failed and the sequence(s) in the fasta file for
# that run is added to a file (given by OUTFILE) in the current directory.

OUTFILE="failed.fasta"

if [ $# -ne 1 ] 
then
    echo
    echo "ERROR: Enter the number of folders to search for index.html:"
    echo "Example: $0 1000"
    echo
    exit 1
fi

for (( x=1; x<=$1; x++ ))
do
    if [ -e $x/project*/html/index.html ]
    then
        echo "$x: index.html present"
    else
        echo "$x: index.html MISSING- adding sequence to $OUTFILE"
        cat $x/$x.fasta >> $OUTFILE
    fi
done