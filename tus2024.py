# %%
# Libraries

import sys
from pathlib import Path
import hashlib
import os

try:
    print('checking if required libraries are installed...')
    import pandas as pd
    import numpy as np
    print('required libraries present!')
except ImportError as errd:
    print(f'Error -> {errd}')
    sys.exit()


# %%
# Function

# Convert time to and time from to activity duration (improved by Lumo)
def getduration(tusdataframe):
    
    """Fully vectorized version using pandas datetime parsing."""
    
    # Parse times to minutes directly
    # Extract hours and minutes using vectorized string methods
    hours_from = pd.to_numeric(tusdataframe['time_from'].str.split(':').str[0], errors='coerce')
    minutes_from = pd.to_numeric(tusdataframe['time_from'].str.split(':').str[1], errors='coerce')
    hours_to = pd.to_numeric(tusdataframe['time_to'].str.split(':').str[0], errors='coerce')
    minutes_to = pd.to_numeric(tusdataframe['time_to'].str.split(':').str[1], errors='coerce')
    
    # Convert to total minutes
    start_minutes = (hours_from * 60) + minutes_from
    end_minutes = (hours_to * 60) + minutes_to
    
    # Overnight detection: end < start AND both are valid
    overnight = start_minutes.notna() & end_minutes.notna() & (end_minutes < start_minutes)
    
    # Calculate duration with overnight correction
    duration = np.where(overnight, (end_minutes + 1440) - start_minutes, end_minutes - start_minutes)
    
    # Invalid if either endpoint is missing
    valid_pairs = start_minutes.notna() & end_minutes.notna()
    duration = np.where(valid_pairs, duration, np.nan)
    
    return duration

# From Lumo by Proton
def gen_huid(df, fsu_col='fsu', hh_col='houshold_nmbr'):
    """
    Generate Household Unique ID from FSU + household number.
    
    Args:
        df: DataFrame containing the columns
        fsu_col: Name of FSU column
        hh_col: Name of household number column
    
    Returns:
        String column: concatenation of fsu + padded household number
    """
    return df[fsu_col].astype(str) + df[hh_col].astype(str).str.zfill(2)

def gen_puid(df, fsu_col='fsu', hh_col='houshold_nmbr', member_col='hhmember_nmbr'):
    """
    Generate Person Unique ID from FSU + household + member number.
    
    Note: Not applicable for Level 1 & 3 (household-level data only)
    """
    return (df[fsu_col].astype(str) + 
            df[hh_col].astype(str).str.zfill(2) + 
            df[member_col].astype(str).str.zfill(2))

# Generate hashes from files
# Source - https://stackoverflow.com/a/3431838
# Posted by quantumSoup, modified by community. See post 'Timeline' for change history
# Retrieved 2026-07-02, License - CC BY-SA 4.0
def dfcheck(df):
    hash_df = hashlib.sha1(pd.util.hash_pandas_object(df).values)
    return hash_df.hexdigest()


# %%
# Code block to take in TUS 2024 file location, read the files, and check files hashes

filelocation = Path(input(prompt="please enter folder location here:"))

try:
    rawhh = pd.read_stata(filelocation/"tus106HH.dta")
    rawper = pd.read_stata(filelocation/"tus106PER.dta")
    rawdates = pd.read_csv(filelocation/"TUS24DOS_DDMMYYYY.TXT", header=None)

    if dfcheck(rawhh)=='07d501794a3c7f6fd7f8dababd871df2e18e4f0a' and dfcheck(rawper)=='2d8b6007b312af3b76514e90a256cf219fe1484a' and dfcheck(rawdates)=='a5224b6b0013de2b281379a0a3b9859c4419e67b':
        print('files look good...')
        rawdates.columns = ['datestring']

    else:
        print('files do not look good! please download the files again and do not edit them!')
        sys.exit()

except Exception as errd: 
    print(f'failed to read files: {errd}')
    sys.exit()


# %%
# Code block to process household level data and dates

print("starting to process data...")

# Creating an empty dataframe and assigning columns from the household level data to it
#region
nhhdata = pd.DataFrame()

nhhdata['sch_id'] = rawhh['Schedule_ID']
nhhdata['fsu'] = rawhh['FSU_Serial_No']
nhhdata['sch'] = rawhh['Schedule']
nhhdata['survey_yr'] = rawhh['Survey_Year']
nhhdata['sector'] = rawhh['Sector']
nhhdata['nssregion'] = rawhh['NSS_Region']
nhhdata['district'] = rawhh['District']
nhhdata['stratum'] = rawhh['Stratum']
nhhdata['substratum'] = rawhh['Sub_Stratum']
nhhdata['subround'] = rawhh['Sub_Round']
nhhdata['fodsubregion'] = rawhh['FOD_Sub_Region']
nhhdata['houshold_nmbr'] = rawhh['Sample_HH_No']
nhhdata['informant_srlno'] = rawhh['Informant_SlNo']
nhhdata['infmnt_resp_code'] = rawhh['Response_Code']
nhhdata['srvy_code'] = rawhh['Survey_Code']
nhhdata['sub_casualtycode'] = rawhh['Reason_for_Substitution']
nhhdata['hhsize'] = rawhh['Household_Size']
nhhdata['relig'] = rawhh['Religion']
nhhdata['castegrp'] = rawhh['Social_Group']
nhhdata['landpossd'] = rawhh['Land_Possessed']
nhhdata['A_usualmnexp'] = rawhh['Exp_Purchase_A']
nhhdata['B_impvalmnhomstck'] = rawhh['Exp_Imputed_B']
nhhdata['C_impvalmninknd'] = rawhh['Exp_Imputed_C']
nhhdata['D_annuexponcloth'] = rawhh['Exp_Clothing_D']
nhhdata['E_annuexpondurbls'] = rawhh['Exp_Durables_E']
nhhdata['A+B+C+(D+E/12)_mnthlyexp'] = rawhh['Monthly_Exp_E_Total']
nhhdata['primsrc_cookng'] = rawhh['Energy_Cooking']
nhhdata['primsrc_lgtng'] = rawhh['Energy_Lighting']
nhhdata['type_washgfclth'] = rawhh['Clothes_Washing_Type']
nhhdata['type_swpngfflr'] = rawhh['Floor_Sweeping_Type']
nhhdata['type_dwlng'] = rawhh['Dwelling_Unit']
nhhdata['type_strctrdwlng'] = rawhh['Structure_Type']
nhhdata['any5yrplusneedspzcare'] = rawhh['Special_Care_Member']
nhhdata['5yrplusspzcareavlbl'] = rawhh['Care_Giver_Available']
nhhdata['canvasstime'] = rawhh['Time_to_Canvass']
nhhdata['nsc'] = rawhh['NSC']
nhhdata['mult'] = rawhh['MULT']

#endregion

del rawhh

# Extracting and attaching dates to the household level data
#region
nhhdata['datejoiner'] = nhhdata['sch_id'] + nhhdata['fsu'] + nhhdata['sch'] + nhhdata['survey_yr'] + nhhdata['sector'] + nhhdata['houshold_nmbr']

rawdates['dateofsurvey'] = rawdates['datestring'].str[-8:].apply(lambda row:row[0:2]+'-'+row[2:4]+'-'+row[4:])

rawdates['datejoiner'] = rawdates['datestring'].str[:-8]

nhhdata = pd.merge(nhhdata, rawdates[['datejoiner', 'dateofsurvey']], on='datejoiner')  

#endregion

del rawdates

# Creating any relevant variables
#region
nhhdata['huid'] = gen_huid(nhhdata)

#endregion

nhhdata = nhhdata[['huid', 'sch_id', 'fsu', 'sch', 'survey_yr', 'sector', 'nssregion', 'district', 'stratum', 'substratum', 'subround', 'fodsubregion', 'houshold_nmbr', 'informant_srlno', 'infmnt_resp_code', 'srvy_code', 'sub_casualtycode', 'hhsize', 'relig', 'castegrp', 'landpossd', 'A_usualmnexp', 'B_impvalmnhomstck', 'C_impvalmninknd', 'D_annuexponcloth', 'E_annuexpondurbls', 'A+B+C+(D+E/12)_mnthlyexp', 'primsrc_cookng', 'primsrc_lgtng', 'type_washgfclth', 'type_swpngfflr', 'type_dwlng', 'type_strctrdwlng', 'any5yrplusneedspzcare', '5yrplusspzcareavlbl', 'dateofsurvey', 'canvasstime', 'nsc', 'mult']]

print("dataset 1/2 done")


# %%
# Code block to process person level data

# Creating an empty dataframe and assigning columns from the person level data to it
#region
nppdata = pd.DataFrame()

nppdata['sch_id'] = rawper['Schedule_ID']
nppdata['fsu'] = rawper['FSU_Serial_No']
nppdata['sch'] = rawper['Schedule']
nppdata['survey_yr'] = rawper['Survey_Year']
nppdata['sector'] = rawper['Sector']
nppdata['nssregion'] = rawper['NSS_Region']
nppdata['district'] = rawper['District']
nppdata['stratum'] = rawper['Stratum']
nppdata['substratum'] = rawper['Sub_Stratum']
nppdata['subround'] = rawper['Sub_Round']
nppdata['fodsubregion'] = rawper['FOD_Sub_Region']
nppdata['houshold_nmbr'] = rawper['Sample_HH_No']
nppdata['hhmember_nmbr'] = rawper['Person_Serial_No']
nppdata['relationtohead'] = rawper['Relation_to_Head']
nppdata['sex'] = rawper['Gender']
nppdata['age'] = rawper['Age']
nppdata['maritalstatus'] = rawper['Marital_Status']
nppdata['max_edu'] = rawper['Highest_Education']
nppdata['upa_code'] = rawper['Principal_Activity_Status']
nppdata['nic2008code'] = rawper['NIC_Industry_Code']
# nppdata['hhmember_nmbr'] = rawper['Member_Serial_No'] # removed as it is repeated
# nppdata['age'] = rawper['Member_Age'] # removed as it is repeated
nppdata['informnt_srlnmbr'] = rawper['Informant_Serial_No']
nppdata['informnt_sex'] = rawper['Informant_Gender']
nppdata['dayofweek'] = rawper['Day_of_Week']
nppdata['typeofday'] = rawper['Type_of_Day']
nppdata['mbr_resp_code'] = rawper['Response_Code']
# nppdata['hhmember_nmbr'] = rawper['Activity_Member_Serial_No'] # removed as it is repeated 
# nppdata['age'] = rawper['Activity_Member_Age'] # removed as it is repeated
nppdata['srlno_activity'] = rawper['Activity_Serial_No']
nppdata['time_from'] = rawper['Time_From']
nppdata['time_to'] = rawper['Time_To']
nppdata['wthr_multactvty'] = rawper['Multiple_Activity_Flag']
nppdata['wthr_simltnactvty'] = rawper['Simultaneous_Activity_Flag']
nppdata['wthr_majoractvty'] = rawper['Major_Activity_Flag']
nppdata['actvtycode'] = rawper['Activity_Code_3Digit']
nppdata['actvtylocation'] = rawper['Activity_Location']
nppdata['paidornot'] = rawper['Unpaid_Paid_Status']
nppdata['entrptype'] = rawper['Enterprise_Type']
nppdata['nsc'] = rawper['NSC']
nppdata['mult'] = rawper['MULT']

#endregion

del rawper

# Creating any relevant variables
#region
nppdata['huid'] = gen_huid(nppdata)

nppdata['puid'] = gen_puid(nppdata)

#endregion

# Making the dataframe wide from long and adding a custom duration column
#region
nppdata['helper'] = nppdata['puid'] + '-' + nppdata['time_from'] + '-' + nppdata['time_to']

nppdata['activity_idx'] = nppdata.groupby('helper').cumcount() + 1

widenppdata = nppdata[['helper', 'activity_idx', 'actvtycode', 'wthr_majoractvty', 'actvtylocation', 'paidornot', 'entrptype']].pivot(
    index=['helper'],
    columns='activity_idx',
    values=['actvtycode', 'wthr_majoractvty', 'actvtylocation', 'paidornot', 'entrptype']
    )

widenppdata.columns = [f'{i}_{j}' for i, j in widenppdata.columns]

widenppdata = widenppdata.reset_index()

widenppdata = pd.merge(widenppdata, nppdata[['huid', 'puid', 'sch_id', 'fsu', 'sch', 'survey_yr', 'sector', 'nssregion', 'district', 'stratum', 'substratum', 'subround', 'fodsubregion', 'houshold_nmbr', 'hhmember_nmbr', 'relationtohead', 'sex', 'age', 'maritalstatus', 'max_edu', 'upa_code', 'nic2008code', 'informnt_srlnmbr', 'informnt_sex', 'dayofweek', 'typeofday', 'mbr_resp_code', 'time_from', 'time_to', 'wthr_multactvty', 'wthr_simltnactvty', 'nsc', 'mult', 'helper']].drop_duplicates(subset=['helper']), on='helper')

widenppdata['activity_duration'] = getduration(widenppdata)

#endregion

del nppdata

widenppdata = widenppdata[['huid', 'puid', 'sch_id', 'fsu', 'sch', 'survey_yr', 'sector', 'nssregion', 'district', 'stratum', 'substratum', 'subround', 'fodsubregion', 'houshold_nmbr', 'hhmember_nmbr', 'relationtohead', 'sex', 'age', 'maritalstatus', 'max_edu', 'upa_code', 'nic2008code', 'informnt_srlnmbr', 'informnt_sex', 'dayofweek', 'typeofday', 'mbr_resp_code', 'time_from', 'time_to', 'activity_duration', 'wthr_multactvty', 'wthr_simltnactvty', 'actvtycode_1', 'actvtycode_2', 'actvtycode_3', 'wthr_majoractvty_1', 'wthr_majoractvty_2', 'wthr_majoractvty_3', 'actvtylocation_1', 'actvtylocation_2', 'actvtylocation_3', 'paidornot_1', 'paidornot_2', 'paidornot_3', 'entrptype_1', 'entrptype_2', 'entrptype_3', 'nsc', 'mult']]

print("dataset 2/2 done")


# %%
# Code block for columndetails

print("starting to process column details...")

# Household level data
shortvarnameshh = ['huid', 'sch_id', 'fsu', 'sch', 'survey_yr', 'sector', 'nssregion', 'district', 'stratum', 'substratum', 'subround', 'fodsubregion', 'houshold_nmbr', 'informant_srlno', 'infmnt_resp_code', 'srvy_code', 'sub_casualtycode', 'hhsize', 'relig', 'castegrp', 'landpossd', 'A_usualmnexp', 'B_impvalmnhomstck', 'C_impvalmninknd', 'D_annuexponcloth', 'E_annuexpondurbls', 'A+B+C+(D+E/12)_mnthlyexp', 'primsrc_cookng', 'primsrc_lgtng', 'type_washgfclth', 'type_swpngfflr', 'type_dwlng', 'type_strctrdwlng', 'any5yrplusneedspzcare', '5yrplusspzcareavlbl', 'dateofsurvey', 'canvasstime', 'nsc', 'mult']

longvarnameshh = ['unique id for the household, not part of original data, derived from fsu+household number', 'schedule id', 'first stage sampling unit (fsu) code', 'schedule', 'survey year', 'whether urban or rural region', 'nss region, first 2 digits represent state and last one represents sub-region in state; for state codes refer to documentation with opencity or microdata', 'code for district, common integer pool (dist 1 of state 1 coded 1, dist 1 of state 2 coded 1 etc) so combine with state code to create unique district codes', 'stratum', 'sub-stratum', 'subround', 'nss field operations division sub-region', 'serial number of household surveyed', 'serial number of the informant', 'informant response code', 'survey code', 'substitution / casualty code', 'size of the household', 'religious affiliation of the household', 'caste or social group affiliation of the household', 'land possessed as on survey date', 'usual consumer expenditure in a month for household purposes out of purchase (a)', 'imputed value of usual consumption in a month from home grown stock (b)', 'imputed value of usual consumption in a month from wages in kind, free collection, gifts, etc (c)', 'expenditure on purchase of items like clothing, footwear etc. during last 365 days (d); not designation of item D changed from durables in 2019 data to clothes in 2024 i.e this data ', 'expenditure on purchase of household durable during last 365 days (e); note this is a new item added to house durable goods exp which was moved from item d in 2019 data to item e in 2025 i.e this data', 'usual monthly consumer expenditure: [a+b+c+(d+6/12)]; note that for 2024 i.e this data monthly exp may increase due to addition of clothes exp so refer to survey documentation of 2019 to see if clothes exp was captured in existing item blocks or not', 'primary energy source for cooking', 'primary energy source for lighting', 'type of washing of clothes', 'type of sweeping of floor', 'whether dwelling owned, rented, no dwelling or other', 'type of structure of dwelling unit', 'if there is a 5 (or 5+) year old who needs special care; note that this splits and partly changes the 2019 equivalent variable <if there is member of age 5 years and above needing special care but no care giver is available>', 'is there any care giver available among the household members for caring of the 5 (or 5+) year old; note that this splits and partly changes the 2019 equivalent variable <if there is member of age 5 years and above needing special care but no care giver is available>', 'date of survey; note date of dispatch variable not there in 2024 public data', 'time to canvass (minutes)', 'nsc', 'mult']

columndetailhh = pd.DataFrame({'variable_name':shortvarnameshh, 'variable_describe':longvarnameshh})

# Person level data
shortvarnamespp = ['huid', 'puid', 'sch_id', 'fsu', 'sch', 'survey_yr', 'sector', 'nssregion', 'district', 'stratum', 'substratum', 'subround', 'fodsubregion', 'houshold_nmbr', 'hhmember_nmbr', 'relationtohead', 'sex', 'age', 'maritalstatus', 'max_edu', 'upa_code', 'nic2008code', 'informnt_srlnmbr', 'informnt_sex', 'dayofweek', 'typeofday', 'mbr_resp_code', 'time_from', 'time_to', 'activity_duration', 'wthr_multactvty', 'wthr_simltnactvty', 'actvtycode_1', 'actvtycode_2', 'actvtycode_3', 'wthr_majoractvty_1', 'wthr_majoractvty_2', 'wthr_majoractvty_3', 'actvtylocation_1', 'actvtylocation_2', 'actvtylocation_3', 'paidornot_1', 'paidornot_2', 'paidornot_3', 'entrptype_1', 'entrptype_2', 'entrptype_3', 'nsc', 'mult']

longvarnamespp = ['unique id for the household, not part of original data, derived from fsu+household number', 'unique id for the member of the household, not part of original data, derived from fsu+household number+household member number', 'schedule id', 'first stage sampling unit (fsu) code', 'schedule', 'survey year', 'whether urban or rural region', 'nss region, first 2 digits represent state and last one represents sub-region in state; for state codes refer to documentation with opencity or microdata', 'code for district, common integer pool (dist 1 of state 1 coded 1, dist 1 of state 2 coded 1 etc) so combine with state code to create unique district codes', 'stratum', 'sub-stratum', 'subround', 'nss field operations division sub-region', 'serial number of household surveyed', 'serial number of member of the household surveyed', 'relation of member to household head', 'sex of member', 'age of member', 'marital status of member', 'highest education of member', 'usual principal activity status of member', 'industry of work of member as per national industrial classification code 2008', 'serial number of the informant', 'sex of the informant', 'day of the week (day before the date of the interview)', 'type of day, regular or not', 'response code for member', 'start time of activity', 'end time of activity', 'duration of activity in minutes NOT PART OF ORIGINAL DATA calcd using time from and time to vars', 'whether multiple activities performed', 'whether multiple activities performed simultaneously', 'activity code for activity #1', 'activity code for activity #2', 'activity code for activity #3', 'whether activity #1 was major activity among the activities in time slot', 'whether activity #2 was major activity among the activities in time slot', 'whether activity #3 was major activity among the activities in time slot', 'location of activity #1', 'location of activity #2', 'location of activity #3', 'whether payment was given for activity #1', 'whether payment was given for activity #2', 'whether payment was given for activity #3', 'type of enterprise for which activity #1 was performed', 'type of enterprise for which activity #2 was performed', 'type of enterprise for which activity #3 was performed', 'nsc', 'mult']

columndetailpp = pd.DataFrame({'variable_name':shortvarnamespp, 'variable_describe':longvarnamespp})

print("column details processed")


# %%
# Code to export the dataframes and columndetails

try:
    os.mkdir(filelocation/'Processed TUS 2024 files')
    print('creating folder and saving files...')
    nhhdata.to_csv(filelocation/'Processed TUS 2024 files'/'householdleveldata.csv', index=False)
    widenppdata.to_csv(filelocation/'Processed TUS 2024 files'/'personleveldata.csv', index=False)
    columndetailhh.to_csv(filelocation/'Processed TUS 2024 files'/'columndetail_hhdata.csv', index=False)
    columndetailpp.to_csv(filelocation/'Processed TUS 2024 files'/'columndetail_psndata.csv', index=False)
    print('all done!')
except PermissionError:
    print('permission denied by system to create folder to save files')
    sys.exit()
except Exception as e:
    print(f'an error occurred while saving output: {e}')
    sys.exit()



