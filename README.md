# Propeller-selection-based-on-APC-data
The following script enables to select a propeller for a UAV, given the flight speed of the UAV and the power required.
The data has been collected from the APC catalogue https://www.apcprop.com/technical-information/performance-data/
The catalogue contains data of 508 propellers. First, the 508 files were combined in a single and robust data file.

Propeller diameter from 4 in to 28 in


# database_APC.py
Combines all the 508 files. Just download the database (https://www.apcprop.com/technical-information/performance-data/), unzip the file, and run the script. 
# propeller_analysis.py
Performs the propeller selection
