# spec-iris-merge-and-qc.md - a specification document for the program iris-merge-and-qc.py

# GOAL
The goal is to create a python program that will combine the iris-all-samples.csv data with a set of identifiers in iris-id-map.csv,
and then use qc information in iris-qc-calls.csv to choose a final set of samples.

# PROGRAM NAME
The resulting python program will be named iris-merge-and-qc.py

# RANDOM SEED
 - use a fixed random seed of 42 for all random operations

# DATA

- use iris-all-samples.csv for a basis for all of this
- do NOT modify the files in data ever
- do not modify iris-all-samples.csv, iris-id-map.csv, iris-qc-calls.csv

# OUTPUTS
 - csv outputs from this should be put in the /data_derived directory
 - json outputs from this should be put in the /outputs directory
 - the py file should be placed in /scripts, NOT /utilities, and is a stand alone py file

 - data_derived/iris-samples-id-mapped.csv and outputs/iris-samples-id-mapped-summary.json 
 	- use iris-all-samples.csv, iris-id-map.csv
 	- use sampleID from iris-all-samples.csv
 	- merge with (inner_join) iris-id-map.csv to give a final file with all columns from
 	  iris-all-samples.csv plus FINAL_ID
 	- output outputs/iris-samples-id-mapped-summary.json with the summarized results of the join:
 		- the number that are unique to each file
 		- the individual IDs (sampleID) for each file that are not in common
 		- the number that are in common
 	- the csv output should eliminate all unpaired combinations, like an inner_join
 	- the final file is csv format for iris-samples-id-mapped.csv
 	

 - data_derived/iris-samples-id-mapped-qc-filtered.csv and outputs/iris-samples-id-mapped-qc-filtered-summary.json
 	- the goal is to create a file with all columns from iris-samples-id-mapped.csv and the QC_CALL from iris-qc-calls.csv
 	- use FINAL_ID from iris-samples-id-mapped.csv
 	- merge with (inner_join) iris-qc-calls.csv to give a final file with all columns from
 	  iris-samples-id-mapped.csv plus QC_CALL
 	- output outputs/iris-samples-id-mapped-qc-filtered-summary.json with the summarized results of the join:
 	 		- the number that are unique to each file
 	 		- the individual IDs (FINAL_ID) for each file that are not in common
 	 		- the number that are in common
 	- the csv output should eliminate all unpaired combinations, like an inner_join 
 	- output to csv

 
 		 
