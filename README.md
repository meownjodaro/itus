# **Minimum Requirements**

1. Python 3.14.3  
   1. Pandas 3.0.5  
   2. Numpy 2.5.2


# **TUS 2019 Download Instructions**

1. Go to [data.opencity.in/dataset/national-time-use-survey-2019](http://data.opencity.in/dataset/national-time-use-survey-2019)  
2. Download the *Level 1*, *Level 2*, *Level 3*, *Level 4*, *Level 5 Part 1*, *Level 5 Part 2*, and *Level 5 Part 3* CSVs / zipped CSVs  
3. Unzip any files that are zipped, move all of them to a new folder, and copy the folder path  
4. Run the Python script for TUS 2019 from your command-line and enter the folder path when prompted  
5. Provided there are no unexpected issues the script will execute, process your data, and spit out processed (and usable) datasets—each one accompanied by a spreadsheet containing the list of columns in the dataset & a brief description of said columns. Execution time should be around 7-8 minutes minimum

The processed Level 5 data[^1] will form the core of your analysis and is at the slot-and-individual level i.e. each row or entry represents one ‘time slot’ in which the activities performed by an individual and related data are recorded. Use the *huid* variable to pull household-level data (from Levels 1 and 3\) and *puid* for individual-level data (from Levels 2 and 4\) to complement your analysis with additional variables.


# **TUS 2024 Download Instructions**

1. Download the survey data and related files from [microdata.gov.in/NADA/index.php/catalog/236/get-microdata](https://microdata.gov.in/NADA/index.php/catalog/236/get-microdata) or use MOSPI’s official Python [package](https://www.mospi.gov.in/unitdata-python-library) to download the files. The dataset’s name as per MOSPI’s record should be *DDI-IND-NSO-TUS-2024-24*
2. Go to where the contents have been downloaded,  
   1. Unzip *TUS2024.zip*  
   2. Install Nesstar using the installer provided in the folder, once that’s done open *TUS2024.Nesstar*  
   3. This will open the TUS 2024 datafile within the Nesstar explorer; on the left-hand side you will find the navigation pane, click on the *\+* sign next to Datasets to expand the directory  
   4. You will now see the two datasets that make up the TUS 2024 datafile, *tus106PER* and *tus106HH*  
   5. To export them from Nesstar, select them by clicking on them and then near the top of the screen click the third button that says ‘*Export Selected Dataset’*  
   6. Create a new folder somewhere on your device and export the datasets as STATA 7 files. Note that this may take some time and interrupting the export midway will result in partially exported files  
3. Unzip *Date of Survey\_TUS2024(which has the household level file structure)* and move *TUS24DOS\_DDMMYYYY.txt* to wherever you’ve exported *tus106PER.dta* and *tus106HH.dta* to
4. Copy the path of the folder containing your exported datasets & text file, run the Python script for TUS 2024 from your command-line, and enter the folder path when prompted  
5. Provided there are no unexpected issues the script will execute, process your data, and spit out processed datasets—each one accompanied by a spreadsheet containing the list of columns in the dataset & a brief description of said columns. Execution time should be around 10-11 minutes minimum

Unlike 2019 data, 2024 TUS data is present in only two files. Household level data records all data collected at the household level while person level data[^2] records all data at the slot-and-individual level i.e. each row or entry represents one ‘time slot’ in which information about the individual (e.g. their age or sex) as well as the activities performed by said individual and related data are recorded. Please note that since individual-level data is condensed to a single dataset, it contains data on both household members for whom time-use data was collected and for whom it was not, the latter having only a single observation and blank values in the time-use related variables.

Use the *huid* variable to merge household level data with individual level data. To be noted is that some survey metadata such as number of investigators and remarks from various survey blocks are not publicly available for this iteration of time use data.


[^1]: *Please note that Level 5 data was transformed from activity-slot-individual level (i.e. each row or entry represented a single activity, recorded at a specific time slot, for a particular individual) to slot-individual level (each row or entry representing a specific time slot, for a particular individual)—as a result of this the activity serial number column, which denoted the order of the activities, was rendered obsolete and thus dropped from the final version of the dataset*

[^2]: *Please note that person level data was transformed from activity-slot-individual level (i.e. each row or entry represented a single activity, recorded at a specific time slot, for a particular individual) to slot-individual level (each row or entry representing a specific time slot, for a particular individual)—as a result of this the activity serial number column, which denoted the order of the activities, was rendered obsolete and thus dropped from the final version of the dataset*