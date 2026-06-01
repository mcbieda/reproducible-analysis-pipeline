# spec-iris-modification.md - a specification document for the program iris-modification.py

# GOAL
The goal is to create a python program that will create a modified iris file with defined characteristics

# PROGRAM NAME
The resulting python program will be named iris-modification.py

# RANDOM SEED
 - use a fixed random seed of 42 for all random operations

# DATA

- iris.data, iris.names
- do NOT modify the files in data ever

# OUTPUTS
 - outputs from this should be put in the /data_derived directory
 - the py file should be placed in /utilities and is a stand alone py file

 - data_derived/iris-original-add-ids.csv
 	- use iris.data and iris.names
 	- add the column names in the first row
 	- add a column called sampleID
 		- for each row, this has a randomly generated sampleID in the format like {upper case letter}-four digit number.
 		- example: Like "C-0472".
 		- The upper case letter must be from A-F
 		- the four digit number must be from 0001 to 8999, and has zeros to begin to always be four digits
 	- the final file is csv format

 - data_derived/iris-simulated-data.csv
 	- the goal is to create simulated data that is like the class data from the original iris data
 	- for each class, calculate the mean of each feature.
 	- using the means for each class and an sd of 0.2, randomly create new samples for each class
 	- for the new samples, round to one decimal place. If a value is negative, set it as 0.0
 	- for the new samples, use a sampleID like above except the number must be from 9000 to 9999
 	- the file should have the same column format etc as the the iris-original-add-ids.csv

 - data_derived/iris-all-samples.csv
 	- combine iris-original-add-ids.csv and iris-simulated-data.csv to make one file. 
 		 
