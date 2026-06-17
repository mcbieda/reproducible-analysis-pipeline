# spec-iris-make-idmap-qc-files.md - a specification document for the program iris-make-map-qc.py

# GOAL
The goal is to create a python program that will create a simulated mapping of id file ("map file") and a qc file.

# PROGRAM NAME
The resulting python program will be named iris-make-map-qc.py

# RANDOM SEED
 - use a fixed random seed of 42 for all random operations

# DATA

- use iris-all-samples.csv for a basis for all of this
- do NOT modify the files in data ever
- do not modify iris-all-samples.csv

# OUTPUTS
 - outputs from this should be put in the /data_derived directory
 - the py file should be placed in /utilities and is a stand alone py file

 - data_derived/iris-id-map.csv
 	- use iris-all-samples.csv
 	- get sampleID from iris-all-samples.csv
 	- randomly eliminate 6 entries
 	- add a column called FINAL_ID
 		- for each row, this has a randomly generated FINAL_ID in the format like FINAL-three digit number.
 		- example: Like "FINAL-008"
 		- the three digit number must be from 001 to 899, and has zeros to begin to always be three digits
 		- each FINAL_ID must be unique
	- create 8 extra rows with simulated sampleID and FINAL_ID
		- simulated sampleIDs follow the same format as above: upper case letter A-F, four digit number 0001-8999
		- simulated sampleIDs must not match any sampleID already present in iris-all-samples.csv or elsewhere in this file
		- simulated FINAL_IDs must not match any FINAL_ID already in this file
 	- the final file is csv format
 

 - data_derived/iris-qc-calls.csv
 	- the goal is to create a file with two columns FINAL_ID and QC_CALL
 	- QC_CALL is either PASS or FAIL
 	- use all the FINAL_ID from iris-id-map.csv, except eliminate 4 randomly
 	- create 6 new FINAL_ID that are different from the FINAL_ID in iris-id-map.csv
 	- only have FAIL for 10% of the samples randomly; the others are all PASS
 	- output to csv

 
 		 
