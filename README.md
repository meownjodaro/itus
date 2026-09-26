# **Requirements**

1. Python 3.14  
   1. Pandas package  
   2. Numpy package


# **TUS 2019 Download Instructions**

1. Go to [data.opencity.in/dataset/national-time-use-survey-2019](http://data.opencity.in/dataset/national-time-use-survey-2019)  
2. Download *Level 1*, *Level 2*, *Level 3*, *Level 4*, *Level 5 Part 1*, *Level 5 Part 2*, and *Level 5 Part 3* CSV files  
3. Unzip any files that are zipped using WinRar or any similar unzipping tool  
4. Move all of the CSV files to a single folder and copy the folder path e.g. *C:/Users/Main/Documents/folderwithCSVs*  
5. Run the Python script for TUS 2019 and enter the folder path when prompted  
6. If there are no issues the script should execute, process your data, and spit out processed data with a spreadsheet with column names & details all contained within a folder saved to where the CSVs are located. Execution time should be around 7-8 minutes minimum

The processed Level 5 data[^1] will form the core of your analysis and is at the slot-and-individual level i.e. each row or entry represents one ‘time slot’ in which the activities performed by an individual and related data are recorded. Use the *huid* variable to pull household-level data (from Levels 1 and 3\) and *puid* for individual-level data (from Levels 2 and 4\) to complement your analysis with additional variables.


# **TUS 2024 Download Instructions**

1. Go to [microdata.gov.in/NADA/index.php/catalog/236/get-microdata](https://microdata.gov.in/NADA/index.php/catalog/236/get-microdata)   
   OR   
   use MOSPI’s official Python [package](https://www.mospi.gov.in/unitdata-python-library) to download the TUS 2024 dataset. The dataset’s name as per MOSPI’s record should be *DDI-IND-NSO-TUS-2024-24*  
2. Go to where the contents have been downloaded,  
   1. Unzip *TUS2024.zip* using Winrar or any similar unzipping tool  
   2. Install Nesstar using the installer provided in the folder, once that’s done open *TUS2024.Nesstar*  
   3. This will open the TUS 2024 datafile within the Nesstar explorer; on the left-hand side you will find the navigation pane, click on the *\+* sign next to Datasets to expand the directory  
   4. You will now see the two datasets that make up the TUS 2024 datafile, *tus106PER* and *tus106HH*  
   5. To export them from Nesstar, select them by clicking on them and then near the top of the screen click the third button that says ‘*Export Selected Dataset’*  
   6. Create a new folder somewhere on your device and export / save the files in *.dta* format  
3. Unzip *Date of Survey\_TUS2024(which has the household level file structure)* and move *TUS24DOS\_DDMMYYYY.txt* to wherever you’ve exported *tus106PER.dta* and *tus106HH.dta*  
4. Copy the folder path e.g. *C:/Users/Main/Documents/folderwithDTAfiles*, run the Python script for TUS 2024, and enter the folder path when prompted  
5. If there are no issues the script should execute, process your data, and spit out processed data with a spreadsheet with column names & details all contained within a folder saved to where the .dta files are located. Execution time should be around 10-11 minutes minimum

Unlike 2019 data, 2024 TUS data is present in only two files. Household level data records all data collected at the household level while person level data[^2] records all data at the slot-and-individual level i.e. each row or entry represents one ‘time slot’ in which information about the individual (e.g. their age or sex) as well as the activities performed by said individual and related data are recorded. Use the *huid* variable to merge household level data with individual level data. To be noted is that some survey metadata such as number of investigators and remarks from various survey blocks are not publicly available for this round of time use data.

[1^]: *Please note that Level 5 data was transformed from activity-slot-individual level (i.e. each row or entry represented a single activity, recorded at a specific time slot, for a particular individual) to slot-individual level (each row or entry representing a specific time slot, for a particular individual)—as a result of this the activity serial number column, which denoted the order of the activities, was rendered obsolete and thus dropped from the final version of the dataset*

[^2]: *Please note that person level data was transformed from activity-slot-individual level (i.e. each row or entry represented a single activity, recorded at a specific time slot, for a particular individual) to slot-individual level (each row or entry representing a specific time slot, for a particular individual)—as a result of this the activity serial number column, which denoted the order of the activities, was rendered obsolete and thus dropped from the final version of the dataset*