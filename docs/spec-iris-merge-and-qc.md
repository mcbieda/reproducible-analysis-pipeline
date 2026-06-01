# SPEC_mergeandqc.md - a specification document for the program iris-merge-and-qc.py

# GOAL
The goal is to create a python program that will combine the iris-combined.csv data with a set of identifiers in iris-mapids.csv,
and then use qc information in iris-qc.csv to choose a final set of samples.

# PROGRAM NAME
The resulting python program will be named iris-merge-and-qc.py

# RANDOM SEED
 - use a fixed random seed of 42 for all random operations

# DATA

- use iris-combined.csv for a basis for all of this
- do NOT modify the files in data ever
- do not modify iris-combined.csv, iris-mapids.csv, iris-qc.csv

# OUTPUTS
 - csv outputs from this should be put in the /data_derived directory
 - json outputs from this should be put in the /outputs directory
 - the py file should be placed in /src, NOT /utilities, and is a stand alone py file

 - data_derived/iris-combined-mapids.csv and outputs/iris-combined-mapids-summary.json 
 	- use iris-combined.csv, iris-mapids.csv
 	- use sampleID from iris-combined.csv
 	- merge with (inner_join) iris-mapids.csv to give a final file with all columns from
 	  iris-combined.csv plus FINAL_ID
 	- output outputs/iris-combined-mapids-summary.json with the summarized results of the join:
 		- the number that are unique to each file
 		- the individual IDs (sampleID) for each file that are not in common
 		- the number that are in common
 	- the csv output should eliminate all unpaired combinations, like an inner_join
 	- the final file is csv format for iris-combined-mapids.csv
 	

 - data_derived/iris-combined-mapids-qc.csv and outputs/iris-combined-mapids-qc-summary.json
 	- the goal is to create a file with all columns from iris-combined-mapids.csv and the QC_CALL from iris-qc.csv
 	- use FINAL_ID from iris-combined-mapids.csv
 	- merge with (inner_join) iris-qc.csv to give a final file with all columns from
 	  iris-combined-mapids.csv plus QC_CALL
 	- output outputs/iris-combined-mapids-qc-summary.json with the summarized results of the join:
 	 		- the number that are unique to each file
 	 		- the individual IDs (FINAL_ID) for each file that are not in common
 	 		- the number that are in common
 	- the csv output should eliminate all unpaired combinations, like an inner_join 
 	- output to csv

 
 		 
