#!/usr/bin/env python

'''
15Oct2015

Extracts taxonomic rankings from SAP (http://ib.berkeley.edu/labs/slatkin/munch/StatisticalAssignmentPackage.html  https://github.com/kaspermunch/sap http://kaspermunch.wordpress.com/software/statistical-assignment-package-sap/)

Takes the html output from SAP and produces a tab separated list of the assignments at the given confidence level

Input is a folder that contains one or more files named index.html in its hierarchy. The folder is searched recursively for index.html files.

If an OTU table is also given, the data from this table is added to the output table

Matthew Kweskin

'''

from bs4 import BeautifulSoup #BeautifulSoup: http://www.crummy.com/software/BeautifulSoup/  Install with:   easy_install beautifulsoup4    or    pip install beautifulsoup4
import sys 
import argparse
import re
import fnmatch
import os


htmlfilename="classic.html"


def readargs():
    '''
    Read in program arguments
    (Mostly copied from: https://github.com/bendmorris/ncbi_taxonomy)
    
    '''

    parser = argparse.ArgumentParser(description="Extracts taxonomic rankings from SAP html output")
    parser.add_argument("FOLDER", help="Folder that contains one or more SAP \""+htmlfilename+"\" output files. The \""+htmlfilename+"\" files can be nested in other files.", type=str)
    parser.add_argument("-out", help="Name of output file of taxonomy (default \"SAP-out.csv\").", type=str, default="SAP-out.csv")
    parser.add_argument("-otutable", help="Name of optional otu table in csv format. If given the OTU data will be added to the taxonomy", type=str)
    parser.add_argument("-l", "--level", help="The cutoff assignment level (default: 80) (possible values: 80, 90, 95).", default=80, type=int)
    parser.add_argument("-p", "--prob", help="OMIT outputting the probability level for each ranking", action='store_false', default=True)
    parser.add_argument("-v", "--verbose", help="Increased verbosity while parsing the html files.", action='store_true', default=False)
    
    args = parser.parse_args()

    #Check args
    if not os.path.isdir(args.FOLDER):
        print("ERROR, folder \""+args.FOLDER+ "\" not found.")
        print
        sys.exit(1)
    
    if args.otutable and not os.path.isfile(args.otutable):
        print("ERROR, OTU table \""+args.otutable+ "\" not found.")
        print
        sys.exit(1)
        
    if args.level not in [80,90,95]:
        print("ERROR, \""+str(args.level)+ "\" is not a valid value for level.")
        print
        sys.exit(1)

    
    return args


def main():
    
    #
    #Get arguments
    #
    args = readargs()
    

    #
    #Read OTU table (if given), store in otutable
    #
    if args.otutable:
        print "Reading otutable: \""+args.otutable+"\""
        with open(args.otutable) as f:
            otutable = [line.strip() for line in f]

    #
    #Find all the index.html files
    #
    print "Searching "+args.FOLDER+" for \""+htmlfilename+"\" files"
    
    indexfiles = []
    for root, dirnames, filenames in os.walk(args.FOLDER):
        for filename in fnmatch.filter(filenames, htmlfilename):
            indexfiles.append(os.path.join(root, filename))
    if not indexfiles:
        print("ERROR, no files named "+htmlfilename+" found in "+args.FOLDER)
        print
        sys.exit(1)
    else:
        print(str(len(indexfiles))+" files named \""+htmlfilename+"\" found")
        print
        
    out = open(args.out,'w')

    ranks=['phylum','class','order','family','genus','species']  #Ignore ranking other than these
    rankings={} #entry for each id, which will have a dictionary of rank and values
    ranksprintprobs=['phylum','class','order']  #Only print probablities for these ranks

    #
    #Extract ranks from each OTU table
    #
    for indexfile in indexfiles:
        startrankingslength = len(rankings)
        
        #Collect data from each file
        print "Searching for \""+str(args.level)+"%\" table in: "+indexfile
        html = open(indexfile)

        #Read in html file into a BeautifulSoup object
        soup = BeautifulSoup(html.read(),"html.parser")


        #Find the text "Assignments at XX%" which is before the tables with the rankings
        assign = soup.find(text=re.compile("Assignments at "+str(args.level)+"%"))
        
        #The table with all the assignement tables (parent.parent was deterined empirically and may change with future SAP releases, if there's a parsing issue, check this)
        assigntabletemp=assign.parent.parent.find('table')
        #A list containing each table with one assignment level
        assigntables=assigntabletemp.find_all('table')
        for assigntable in assigntables:
            #h3 text in the table has the rank 
            currrank=assigntable.h3.string
            if args.verbose:
                print("-----Collecting: "+currrank)
            #Get all the table rows in the assignment table
            trstemp=assigntable.find("tr")
            trs=trstemp.find_all("tr")
            for tr in trs:
                #Get all the table cell for that row
                tds=tr.find_all("td")
                for td in tds:
                    #print td
                    #Get all the a tags in the cell (if there are any, this will skip table cells that aren't related to assignment)
                    ayes=td.find_all("a")
                    for a in ayes:
                        #Get the full <a> tag. a.string should work, but some of the anchor tags aren't being parsed correctly so using a regex to extract text from <a> tag
                        astring=str(a)
                        #print "orig: "+astring
                        #The href for the sample id starts with "clones"
                        if re.search('href="clones',astring) is not None:
                            #parse the anchor- first group (between first > and :) is the taxon id, second group is the % match
                            tempid=re.search('>([^ :]+):....(.*?)%',astring)
                            if tempid:
                                currid=tempid.group(1)
                                if args.verbose:
                                    print currid + " " + currname + " " + tempid.group(2)
                                if currid not in rankings:
                                    rankings[currid]={}
                                rankings[currid][currrank]=currname    #Add the rank and identifiation to the rankings dictionary
                                rankings[currid][currrank+"_level"]=tempid.group(2)    #Add the ranking level
                        if re.search('href="http://www.ncbi.nlm.nih.gov',astring) is not None:    #Links for identification start with "http://www.ncbi.nlm.nih.gov"
                            #Get the text from the entire <a> anchor text
                            tempname=re.search('>(.*)<',astring)
                            if tempname:
                                currname=tempname.group(1)
        print ("  found "+str(len(rankings)-startrankingslength)+" taxa in file")
        print


    #
    #Output the results as a comma seperated list
    #
    
    #print header line of csv
    for rank in ranks:
        out.write(","+rank)
        if args.prob:
            out.write(","+rank+"_level")
    if args.otutable:
        out.write(otutable.pop(0))  #NEED TO REMOVE FIRST ","
    out.write("\n")


    #print csv table (when OTU table NOT provided)
    if not args.otutable:
        for ranking in rankings:
            out.write(ranking) #Taxon ID
            for rank in ranks:
                if rank in rankings[ranking]:
                    out.write(","+rankings[ranking][rank]) #Print taxon for rank
                    if args.prob and rank in ranksprintprobs:
                        out.write(","+rankings[ranking][rank+"_level"]+"%") #Print ranking level
                else:
                    #This is if the ranking isn't available for this sample
                    out.write(",")
                    if args.prob and rank in ranksprintprobs:
                        out.write(",")
            out.write("\n")

    #print csv table (when OTU table IS provided)
    if args.otutable:
        for tableline in otutable:
            #Print id,taxonomy,OTU data
            tableline_split=tableline.split(",")
            temp_output_id=re.search('[^>].*',tableline_split[0])
            curr_output_id=temp_output_id.group(0)
            out.write(tableline_split.pop(0))
            for rank in ranks:
                if curr_output_id in rankings and rank in rankings[curr_output_id]:
                    out.write(","+rankings[curr_output_id][rank]) #print taxon for rank (if available)
                    if args.prob and rank in ranksprintprobs:
                        out.write(","+rankings[curr_output_id][rank+"_level"]+"%") #Print ranking level
                else:
                    #This is if the ranking isn't available for this sample
                    out.write(",")
                    if args.prob and rank in ranksprintprobs:
                        out.write(",")
            
            out.write(','+','.join(tableline_split))
            out.write("\n")
            
    print str(len(rankings))+" identifications found in \""+args.FOLDER+"\""
    
    if args.otutable:
        print str(len(otutable))+" id numbers found OTU table \""+args.otutable+"\""

    print "Output file: \""+args.out+"\""
        

if __name__ == '__main__':
    main()
