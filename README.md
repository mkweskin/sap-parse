#Utilities for SAP (Statistical Assignment Package)
These are scripts that can be used with [Statistical Assignment Package](https://github.com/kaspermunch/sap/).
The scripts are geared toward running SAP jobs in parallel on a computing cluster. A large fasta file can be split into individual sequences and each sequence run separately on the cluster. 



##split-and-run.pl and SAP-batch.job
*split-and-run.pl* takes a fasta file, splits each sequence into a sequentially number fasta file, each in its own directory. It submits a qsub command *SAP-batch.job* for each fasta file. *SAP-batch.job* should be modified for your cluster, SAP command options, and your email address for the -e SAP option.

```
./split-and-run.pl input.fasta
```
If input.fasta has 10 sequences, it creates directories named 1 though 10 each with a fasta file named 1.fasta through 10.fasta.


##find-failed.sh
Use this after running *split-and-run.pl* and your jobs have completed. This script will find runs that have not completed. It looks for the file `index.html` in each sequentially numbered directory. If `index.html` is missing, the fasta file from that directory is added to a file *failed.fasta* for resubmission with the split-and-run.pl script.

Check directories 1 through 10 for *index.html*
```
./find-failed.sh 10
```

##SAP-parse-all-files.py
This finds all SAP output files in the given directory, extracts the assignments made and outputs a csv file summarizing the results. It can take an existing csv (e.g. otutable) file that has matching ID numbers to the SAP output and combine this csv table with the new sap data. Note, this script requires the Python package [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/) which can be installed with `easy_install beautifulsoup4` or `pip install beautifulsoup4` on many systems.

```
usage: SAP-parse-all-files.py [-h] [-out OUT] [-otutable OTUTABLE]
                                        [-l LEVEL] [-p] [-v]
                                        DIRECTORY

Extracts taxonomic rankings from SAP html output

positional arguments:
  DIRECTORY                Directory that contains one or more SAP "classic.html"
                        output files. The "classic.html" files can be nested
                        in other files.

optional arguments:
  -h, --help            show this help message and exit
  -out OUT              Name of output file of taxonomy (default "SAP-
                        out.csv").
  -otutable OTUTABLE    Name of optional otu table in csv format. If given the
                        OTU data will be added to the taxonomy
  -l LEVEL, --level LEVEL
                        The cutoff assignment level (default: 80) (possible
                        values: 80, 90, 95).
  -p, --prob            OMIT outputting the probability level for each ranking
  -v, --verbose         Increased verbosity while parsing the html files.
 ```