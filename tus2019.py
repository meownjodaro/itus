# %%
# Libraries

import sys
from pathlib import Path
import hashlib
import csv
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
# All functions

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

# Generate hashes from files
# Source - https://stackoverflow.com/a/3431838
# Posted by quantumSoup, modified by community. See post 'Timeline' for change history
# Retrieved 2026-07-02, License - CC BY-SA 4.0
def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

# From Lumo by Proton
def load_custom_header_csv(filepath, column_names):
    """
    Read CSV ignoring original headers, applying custom column names.
    Includes pandas' built-in error checking while allowing custom schema.
    
    Args:
        filepath: Path to CSV file
        column_names: List of desired column names
    
    Returns:
        DataFrame with custom column names
    """
    kwargs = {
        'header': None,           # Ignore original header
        'names': column_names,    # Apply custom headers
        'na_values': [''],        # Convert '' to NaN
        'skiprows': 1,          # Skip the original header row (row 0)
    }
        
    df = pd.read_csv(filepath, **kwargs)
    return df

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

def gen_nssregion(df, state_col='state_first2dgtsofnssregion', region_col='region_lastdgtofnssregion'):
    """
    Combine state + sub-region into NSS region code.
    
    First 2 digits = state, last digit = sub-region within state.
    """
    return ((df[state_col].astype(str) + df[region_col].astype(str))
            .astype('Int64'))

def assign_ids(df, level):
    """
    Apply appropriate ID generation based on data level.
    
    Args:
        df: Input DataFrame
        level: 1-5 indicating data hierarchy
    
    Returns:
        DataFrame with huid, puid (if applicable), nssregion added
    """
    df = df.copy()
    df['huid'] = gen_huid(df)
    df['nssregion'] = gen_nssregion(df)
    
    # Only Levels 2, 4, 5 have person-level IDs
    if level in [2, 4, 5]:
        df['puid'] = gen_puid(df)
    
    return df


# %%
# Code block to take in TUS 2019 file location

filelocation = Path(input(prompt="please enter folder location here:"))

level1 = filelocation/"6bce1afd-a463-4647-bb2e-a71ed38d7caf.csv"

level2 = filelocation/"4f5b05d0-cfb8-4edc-a7c3-a6c0dc5e6fbb.csv"

level3 = filelocation/"f1828537-0f08-41e1-a8e7-b1510f402ee8.csv"

level4 = filelocation/"dc19cf29-b727-4ea6-8119-55792335f5fa.csv"

level5part1 = filelocation/"TUS106_L05_1.csv"

level5part2 = filelocation/"TUS106_L05_2.csv"

level5part3 = filelocation/"TUS106_L05_3.csv"


# %%
# Code block to check file hashes

if md5(level1)=='8b3672764c4f5930a32ebb6b129e510b' and md5(level2)=='d41ed7fddfb81d6469214b5b4f5e84bc' and md5(level3)=='31a054bde7a981d21ecb6156f183a5c3' and md5(level4)=='785ddfa45c9056d11b44b10e28314c62' and md5(level5part1)=='1bee3bb7261d538ee4e4841975764938' and md5(level5part2)=='284f21f3b52ca6ceb1ff686e281f01a7' and md5(level5part3)=='94da4d8787f719788ffeef9c8fbfbb60':
    print('files look good...')
else:
    print('files do not look good! please download the files again and do not edit them!')
    sys.exit()


# %%
# Code block to process Lvl 1

print("starting to process data...")

lvl1customheaders = ['sch_id', 'fsu', 'sch', 'survey_yr', 'sector', 'state_first2dgtsofnssregion', 'region_lastdgtofnssregion', 'district', 'stratum', 'substratum', 'subround', 'fodsubregion', 'houshold_nmbr', 'level', 'filler', 'informant_srlno', 'infmnt_resp_code', 'srvy_code', 'sub_casualtycode', 'filler2', 'dateofsurvey', 'dateofdispatch', 'canvasstime', 'noofinvestigators', 'rmrksinblock7', 'rmrksinblock8', 'rmrkselsewhere', 'rmrkselsewhere2', 'filler3', 'nsc', 'mult']

nlevel1 = load_custom_header_csv(level1, lvl1customheaders)

nlevel1 = nlevel1.drop(columns=['filler', 'filler2', 'filler3'])

for col in ['informant_srlno', 'sub_casualtycode', 'dateofsurvey', 'dateofdispatch', 'canvasstime']:
    nlevel1.loc[nlevel1[col] == '', col] = np.nan

nlevel1.loc[(nlevel1['noofinvestigators']=='') | (nlevel1['noofinvestigators']=='*'), 'noofinvestigators'] = np.nan

nlevel1 = nlevel1.astype({'sch_id':'str', 'fsu':'Int64', 'sch':'Int64', 'survey_yr':'Int64', 'sector':'Int64', 'state_first2dgtsofnssregion':'Int64', 'region_lastdgtofnssregion':'Int64', 'district':'Int64', 'stratum':'Int64', 'substratum':'Int64', 'subround':'Int64', 'fodsubregion':'str', 'houshold_nmbr':'Int64', 'level':'Int64', 'informant_srlno':'Int64', 'infmnt_resp_code':'Int64', 'srvy_code':'Int64', 'sub_casualtycode':'Int64', 'dateofsurvey':'Int64', 'dateofdispatch':'Int64', 'canvasstime':'Int64', 'noofinvestigators':'Int64', 'rmrksinblock7':'Int64', 'rmrksinblock8':'Int64', 'rmrkselsewhere':'Int64', 'rmrkselsewhere2':'Int64', 'nsc':'Int64', 'mult':'Int64'}, errors='ignore')

nlevel1 = assign_ids(nlevel1, 1)

nlevel1 = nlevel1[['huid', 'sch_id', 'fsu', 'sch', 'survey_yr', 'sector', 'nssregion', 'district', 'stratum', 'substratum', 'subround', 'fodsubregion', 'houshold_nmbr', 'level', 'informant_srlno', 'infmnt_resp_code', 'srvy_code', 'sub_casualtycode', 'dateofsurvey', 'dateofdispatch', 'canvasstime', 'noofinvestigators', 'rmrksinblock7', 'rmrksinblock8', 'rmrkselsewhere', 'rmrkselsewhere2', 'nsc', 'mult']]

print("dataset 1/5 done")


# %%
# Code block to process Lvl 2

lvl2customheaders = ['sch_id', 'fsu', 'sch', 'survey_yr', 'sector', 'state_first2dgtsofnssregion', 'region_lastdgtofnssregion', 'district', 'stratum', 'substratum', 'subround', 'fodsubregion', 'houshold_nmbr', 'level', 'filler', 'hhmember_nmbr', 'relationtohead', 'sex', 'age', 'maritalstatus', 'max_edu', 'upa_code', 'nic2008code', 'filler2', 'nsc', 'mult']

nlevel2 = load_custom_header_csv(level2, lvl2customheaders)

nlevel2 = nlevel2.drop(columns=['filler', 'filler2'])

for col in ['relationtohead', 'max_edu', 'upa_code', 'nic2008code']:
    nlevel2.loc[nlevel2[col] == '', col] = np.nan

nlevel2 = nlevel2.astype({'sch_id':'str', 'fsu':'Int64', 'sch':'Int64', 'survey_yr':'Int64', 'sector':'Int64', 'state_first2dgtsofnssregion':'Int64', 'region_lastdgtofnssregion':'Int64', 'district':'Int64', 'stratum':'Int64', 'substratum':'Int64', 'subround':'Int64', 'fodsubregion':'str', 'houshold_nmbr':'Int64', 'level':'Int64', 'hhmember_nmbr':'Int64', 'relationtohead':'Int64', 'sex':'Int64', 'age':'Int64', 'maritalstatus':'Int64', 'max_edu':'Int64', 'upa_code':'Int64', 'nic2008code':'Int64', 'nsc':'Int64', 'mult':'Int64'})

nlevel2 = assign_ids(nlevel2, 2)

nlevel2 = nlevel2[['huid', 'puid', 'sch_id', 'fsu', 'sch', 'survey_yr', 'sector', 'nssregion', 'district', 'stratum', 'substratum', 'subround', 'fodsubregion', 'houshold_nmbr', 'level', 'hhmember_nmbr', 'relationtohead', 'sex', 'age', 'maritalstatus', 'max_edu', 'upa_code', 'nic2008code', 'nsc', 'mult']]

print("dataset 2/5 done")


# %%
# Code block to process Lvl 3

lvl3customheaders = ['sch_id', 'fsu', 'sch', 'survey_yr', 'sector', 'state_first2dgtsofnssregion', 'region_lastdgtofnssregion', 'district', 'stratum', 'substratum', 'subround', 'fodsubregion', 'houshold_nmbr', 'level', 'filler', 'hhsize', 'relig', 'castegrp', 'landpossd', 'A_usualmnexp', 'B_impvalmnhomstck', 'C_impvalmninknd', 'D_annuexpondurbls', 'A+B+C+D/12_mnthlyexp', 'primsrc_cookng', 'primsrc_lgtng', 'type_washgfclth', 'type_swpngfflr', 'type_strctrdwlng', 'any5yrplusneedbutnospzcare', 'filler2', 'nsc', 'mult']

nlevel3 = load_custom_header_csv(level3, lvl3customheaders)

nlevel3 = nlevel3.drop(columns=['filler', 'filler2'])

for col in ['landpossd', 'A_usualmnexp', 'B_impvalmnhomstck', 'C_impvalmninknd', 'D_annuexpondurbls', 'A+B+C+D/12_mnthlyexp', 'any5yrplusneedbutnospzcare']:
    nlevel3.loc[nlevel3[col] == '', col] = np.nan

nlevel3 = nlevel3.astype({'sch_id':'str', 'fsu':'Int64', 'sch':'Int64', 'survey_yr':'Int64', 'sector':'Int64', 'state_first2dgtsofnssregion':'Int64', 'region_lastdgtofnssregion':'Int64', 'district':'Int64', 'stratum':'Int64', 'substratum':'Int64', 'subround':'Int64', 'fodsubregion':'str', 'houshold_nmbr':'Int64', 'level':'Int64', 'hhsize':'Int64', 'relig':'Int64', 'castegrp':'Int64', 'landpossd':'Int64', 'A_usualmnexp':'Int64', 'B_impvalmnhomstck':'Int64', 'C_impvalmninknd':'Int64', 'D_annuexpondurbls':'Int64', 'A+B+C+D/12_mnthlyexp':'Int64', 'primsrc_cookng':'Int64', 'primsrc_lgtng':'Int64', 'type_washgfclth':'Int64', 'type_swpngfflr':'Int64', 'type_strctrdwlng':'Int64', 'any5yrplusneedbutnospzcare':'Int64', 'nsc':'Int64', 'mult':'Int64'})

nlevel3 = assign_ids(nlevel3, 3)

nlevel3 = nlevel3[['huid', 'sch_id', 'fsu', 'sch', 'survey_yr', 'sector', 'nssregion', 'district', 'stratum', 'substratum', 'subround', 'fodsubregion', 'houshold_nmbr', 'level', 'hhsize', 'relig', 'castegrp', 'landpossd', 'A_usualmnexp', 'B_impvalmnhomstck', 'C_impvalmninknd', 'D_annuexpondurbls', 'A+B+C+D/12_mnthlyexp', 'primsrc_cookng', 'primsrc_lgtng', 'type_washgfclth', 'type_swpngfflr', 'type_strctrdwlng', 'any5yrplusneedbutnospzcare', 'nsc', 'mult']]

print("dataset 3/5 done")


# %%
# Code block to process Lvl 4

lvl4customheaders = ['sch_id', 'fsu', 'sch', 'survey_yr', 'sector', 'state_first2dgtsofnssregion', 'region_lastdgtofnssregion', 'district', 'stratum', 'substratum', 'subround', 'fodsubregion', 'houshold_nmbr', 'level', 'filler', 'hhmember_nmbr', 'age', 'relationtoinformnt', 'dayofweek', 'typeofday', 'mbr_resp_code', 'filler2', 'nsc', 'mult']

nlevel4 = load_custom_header_csv(level4, lvl4customheaders)

nlevel4 = nlevel4.drop(columns=['filler', 'filler2'])

for col in ['dayofweek', 'typeofday', 'mbr_resp_code']:
    nlevel4.loc[nlevel4[col] == '', col] = np.nan

nlevel4 = nlevel4.astype({'sch_id':'str', 'fsu':'Int64', 'sch':'Int64', 'survey_yr':'Int64', 'sector':'Int64', 'state_first2dgtsofnssregion':'Int64', 'region_lastdgtofnssregion':'Int64', 'district':'Int64', 'stratum':'Int64', 'substratum':'Int64', 'subround':'Int64', 'fodsubregion':'str', 'houshold_nmbr':'Int64', 'level':'Int64', 'hhmember_nmbr':'Int64', 'age':'Int64', 'relationtoinformnt':'str', 'dayofweek':'Int64', 'typeofday':'Int64', 'mbr_resp_code':'Int64', 'nsc':'Int64', 'mult':'Int64'})

nlevel4 = assign_ids(nlevel4, 4)

nlevel4 = nlevel4[['huid', 'puid', 'sch_id', 'fsu', 'sch', 'survey_yr', 'sector', 'nssregion', 'district', 'stratum', 'substratum', 'subround', 'fodsubregion', 'houshold_nmbr', 'level', 'hhmember_nmbr', 'age', 'relationtoinformnt', 'dayofweek', 'typeofday', 'mbr_resp_code', 'nsc', 'mult']]

print("dataset 4/5 done")


# %%
# Code block to process Lvl 5

listoflvl5prtlocs = [level5part1, level5part2, level5part3]

listoflvl5prtdfms = []

for lvl5prtloc in listoflvl5prtlocs:
    lvl5customheaders = ['sch_id', 'fsu', 'sch', 'survey_yr', 'sector', 'state_first2dgtsofnssregion', 'region_lastdgtofnssregion', 'district', 'stratum', 'substratum', 'subround', 'fodsubregion', 'houshold_nmbr', 'level', 'filler', 'hhmember_nmbr', 'age', 'srlno_activity', 'time_from', 'time_to', 'wthr_multactvty', 'wthr_simltnactvty', 'wthr_majoractvty', 'actvtycode', 'actvtylocation', 'paidornot', 'entrptype', 'filler2', 'nsc', 'mult']

    nlevel5px = load_custom_header_csv(lvl5prtloc, lvl5customheaders)

    nlevel5px = nlevel5px.drop(columns=['filler', 'filler2'])

    for col in ['wthr_multactvty', 'wthr_simltnactvty', 'entrptype']:
        nlevel5px.loc[nlevel5px[col] == '', col] = np.nan

    nlevel5px[['nsc', 'mult']] = nlevel5px['mult'].str.split(expand=True)

    nlevel5px = nlevel5px.astype({'sch_id':'str', 'fsu':'Int64', 'sch':'Int64', 'survey_yr':'Int64', 'sector':'Int64', 'state_first2dgtsofnssregion':'Int64', 'region_lastdgtofnssregion':'Int64', 'district':'Int64', 'stratum':'Int64', 'substratum':'Int64', 'subround':'Int64', 'fodsubregion':'str', 'houshold_nmbr':'Int64', 'level':'Int64', 'hhmember_nmbr':'Int64', 'age':'Int64', 'srlno_activity':'Int64', 'time_from':'str', 'time_to':'str', 'wthr_multactvty':'Int64', 'wthr_simltnactvty':'Int64', 'wthr_majoractvty':'Int64', 'actvtycode':'Int64', 'actvtylocation':'Int64', 'paidornot':'Int64', 'entrptype':'Int64', 'nsc':'Int64', 'mult':'Int64'})

    nlevel5px = assign_ids(nlevel5px, 5)
    
    nlevel5px = nlevel5px[['huid', 'puid', 'sch_id', 'fsu', 'sch', 'survey_yr', 'sector', 'nssregion', 'district', 'stratum', 'substratum', 'subround', 'fodsubregion', 'houshold_nmbr', 'level', 'hhmember_nmbr', 'age', 'srlno_activity', 'time_from', 'time_to', 'wthr_multactvty', 'wthr_simltnactvty', 'wthr_majoractvty', 'actvtycode', 'actvtylocation', 'paidornot', 'entrptype', 'nsc', 'mult']]

    listoflvl5prtdfms.append(nlevel5px)

nlevel5 = pd.concat([listoflvl5prtdfms[0], listoflvl5prtdfms[1], listoflvl5prtdfms[2]])

nlevel5.drop(nlevel5.index[-1], inplace=True)

del listoflvl5prtdfms

nlevel5['helper'] = nlevel5['puid'] + '-' + nlevel5['time_from'] + '-' + nlevel5['time_to']

nlevel5['activity_idx'] = nlevel5.groupby('helper').cumcount() + 1

widenlevel5 = nlevel5[['helper', 'activity_idx', 'actvtycode', 'wthr_majoractvty', 'actvtylocation', 'paidornot', 'entrptype']].pivot(
    index=['helper'],
    columns='activity_idx',
    values=['actvtycode', 'wthr_majoractvty', 'actvtylocation', 'paidornot', 'entrptype']
    )

widenlevel5.columns = [f'{i}_{j}' for i, j in widenlevel5.columns]

widenlevel5 = widenlevel5.reset_index()

widenlevel5 = pd.merge(widenlevel5, nlevel5[['huid', 'puid', 'sch_id', 'fsu', 'sch', 'survey_yr', 'sector', 'nssregion', 'district', 'stratum', 'substratum', 'subround', 'fodsubregion', 'houshold_nmbr', 'level', 'hhmember_nmbr', 'age', 'time_from', 'time_to', 'wthr_multactvty', 'wthr_simltnactvty', 'nsc', 'mult', 'helper']].drop_duplicates(subset='helper'), on='helper')

del nlevel5

widenlevel5['activity_duration'] = getduration(widenlevel5)

widenlevel5 = widenlevel5[['huid', 'puid', 'sch_id', 'fsu', 'sch', 'survey_yr', 'sector', 'nssregion', 'district', 'stratum', 'substratum', 'subround', 'fodsubregion', 'houshold_nmbr', 'level', 'hhmember_nmbr', 'age', 'time_from', 'time_to', 'activity_duration', 'wthr_multactvty', 'wthr_simltnactvty', 'actvtycode_1', 'actvtycode_2', 'actvtycode_3', 'wthr_majoractvty_1', 'wthr_majoractvty_2', 'wthr_majoractvty_3', 'actvtylocation_1', 'actvtylocation_2', 'actvtylocation_3', 'paidornot_1', 'paidornot_2', 'paidornot_3', 'entrptype_1', 'entrptype_2', 'entrptype_3', 'nsc', 'mult']]

print("dataset 5/5 done")


# %%
# Code block for columndetails

print("starting to process column details...")

# Level 1
shortvarnameslvl1 = ['huid', 'sch_id', 'fsu', 'sch', 'survey_yr', 'sector', 'nssregion', 'district', 'stratum', 'substratum', 'subround', 'fodsubregion', 'houshold_nmbr', 'level', 'informant_srlno', 'infmnt_resp_code', 'srvy_code', 'sub_casualtycode', 'dateofsurvey', 'dateofdispatch', 'canvasstime', 'noofinvestigators', 'rmrksinblock7', 'rmrksinblock8', 'rmrkselsewhere', 'rmrkselsewhere2', 'nsc', 'mult'] 

longvarnameslvl1 = ['unique id for the household, not part of original data, derived from fsu+household number', 'schedule id', 'first stage sampling unit (fsu) code', 'schedule', 'survey year', 'whether urban or rural region', 'nss region, first 2 digits represent state and last one represents sub-region in state; for state codes refer to documentation with opencity or microdata', 'code for district, common integer pool (dist 1 of state 1 coded 1, dist 1 of state 2 coded 1 etc) so combine with state code to create unique district codes', 'stratum', 'sub-stratum', 'subround', 'nss field operations division sub-region', 'serial number of household surveyed', 'level of data, in this case 1', 'serial number of the informant', 'informant response code', 'survey code', 'substitution / casualty code', 'date of survey', 'date of dispatch', 'time to canvass (minutes)', 'no of investigators in the team', 'remarks in block 7', 'remarks in block 8', 'remarks elsewhere in schedule', 'remarks elsewhere in schedule', 'nsc', 'mult']

columndetaillvl1 = pd.DataFrame({'variable_name':shortvarnameslvl1, 'variable_describe':longvarnameslvl1})

# Level 2
shortvarnameslvl2 = ['huid', 'puid', 'sch_id', 'fsu', 'sch', 'survey_yr', 'sector', 'nssregion', 'district', 'stratum', 'substratum', 'subround', 'fodsubregion', 'houshold_nmbr', 'level', 'hhmember_nmbr', 'relationtohead', 'sex', 'age', 'maritalstatus', 'max_edu', 'upa_code', 'nic2008code', 'nsc', 'mult']

longvarnameslvl2 = ['unique id for the household, not part of original data, derived from fsu+household number', 'unique id for the member of the household, not part of original data, derived from fsu+household number+household member number', 'schedule id', 'first stage sampling unit (fsu) code', 'schedule', 'survey year', 'whether urban or rural region', 'nss region, first 2 digits represent state and last one represents sub-region in state; for state codes refer to documentation with opencity or microdata', 'code for district, common integer pool (dist 1 of state 1 coded 1, dist 1 of state 2 coded 1 etc) so combine with state code to create unique district codes', 'stratum', 'sub-stratum', 'subround', 'nss field operations division sub-region', 'serial number of household surveyed', 'level of data, in this case 2', 'serial number of member of the household surveyed', 'relation of member to household head', 'sex of member', 'age of member', 'marital status of member', 'highest education of member', 'usual principal activity status of member', 'industry of work of member as per national industrial classification code 2008', 'nsc', 'mult']

columndetaillvl2 = pd.DataFrame({'variable_name':shortvarnameslvl2, 'variable_describe':longvarnameslvl2})

# Level 3
shortvarnameslvl3 = ['huid', 'sch_id', 'fsu', 'sch', 'survey_yr', 'sector', 'nssregion', 'district', 'stratum', 'substratum', 'subround', 'fodsubregion', 'houshold_nmbr', 'level', 'hhsize', 'relig', 'castegrp', 'landpossd', 'A_usualmnexp', 'B_impvalmnhomstck', 'C_impvalmninknd', 'D_annuexpondurbls', 'A+B+C+D/12_mnthlyexp', 'primsrc_cookng', 'primsrc_lgtng', 'type_washgfclth', 'type_swpngfflr', 'type_strctrdwlng', 'any5yrplusneedbutnospzcare', 'nsc', 'mult']

longvarnameslvl3 = ['unique id for the household, not part of original data, derived from fsu+household number', 'schedule id', 'first stage sampling unit (fsu) code', 'schedule', 'survey year', 'whether urban or rural region', 'nss region, first 2 digits represent state and last one represents sub-region in state; for state codes refer to documentation with opencity or microdata', 'code for district, common integer pool (dist 1 of state 1 coded 1, dist 1 of state 2 coded 1 etc) so combine with state code to create unique district codes', 'stratum', 'sub-stratum', 'subround', 'nss field operations division sub-region', 'serial number of household surveyed', 'level of data, in this case 3', 'size of the household', 'religious affiliation of the household', 'caste or social group affiliation of the household', 'land possessed as on survey date', 'usual consumer expenditure in a month for household purposes out of purchase (a)', 'imputed value of usual consumption in a month from home grown stock (b)', 'imputed value of usual consumption in a month from wages in kind, free collection, gifts, etc (c)', 'expenditure on purchase of household durable during last 365 days (d)', 'usual monthly consumer expenditure: [a+b+c+(d/12)]', 'primary energy source for cooking', 'primary energy source for lighting', 'type of washing of clothes', 'type of sweeping of floor', 'type of structure of dwelling unit', 'if there is member of age 5 years and above needing special care but no care giver is available', 'nsc', 'mult']

columndetaillvl3 = pd.DataFrame({'variable_name':shortvarnameslvl3, 'variable_describe':longvarnameslvl3})

# Level 4
shortvarnameslvl4 = ['huid', 'puid', 'sch_id', 'fsu', 'sch', 'survey_yr', 'sector', 'nssregion', 'district', 'stratum', 'substratum', 'subround', 'fodsubregion', 'houshold_nmbr', 'level', 'hhmember_nmbr', 'age', 'relationtoinformnt', 'dayofweek', 'typeofday', 'mbr_resp_code', 'nsc', 'mult']

longvarnameslvl4 = ['unique id for the household, not part of original data, derived from fsu+household number', 'unique id for the member of the household, not part of original data, derived from fsu+household number+household member number', 'schedule id', 'first stage sampling unit (fsu) code', 'schedule', 'survey year', 'whether urban or rural region', 'nss region, first 2 digits represent state and last one represents sub-region in state; for state codes refer to documentation with opencity or microdata', 'code for district, common integer pool (dist 1 of state 1 coded 1, dist 1 of state 2 coded 1 etc) so combine with state code to create unique district codes', 'stratum', 'sub-stratum', 'subround', 'nss field operations division sub-region', 'serial number of household surveyed', 'level of data, in this case 4', 'serial number of member of the household surveyed', 'age of member', 'relation of informant with household member', 'day of the week (day before the date of the interview)', 'type of day, regular or not', 'response code for member', 'nsc', 'mult']

columndetaillvl4 = pd.DataFrame({'variable_name':shortvarnameslvl4, 'variable_describe':longvarnameslvl4})

# Level 5
shortvarnameslvl5 = ['huid', 'puid', 'sch_id', 'fsu', 'sch', 'survey_yr', 'sector', 'nssregion', 'district', 'stratum', 'substratum', 'subround', 'fodsubregion', 'houshold_nmbr', 'level', 'hhmember_nmbr', 'age', 'time_from', 'time_to', 'activity_duration', 'wthr_multactvty', 'wthr_simltnactvty', 'actvtycode_1', 'actvtycode_2', 'actvtycode_3', 'wthr_majoractvty_1', 'wthr_majoractvty_2', 'wthr_majoractvty_3', 'actvtylocation_1', 'actvtylocation_2', 'actvtylocation_3', 'paidornot_1', 'paidornot_2', 'paidornot_3', 'entrptype_1', 'entrptype_2', 'entrptype_3', 'nsc', 'mult']

longvarnameslvl5 = ['unique id for the household, not part of original data, derived from fsu+household number', 'unique id for the member of the household, not part of original data, derived from fsu+household number+household member number', 'schedule id', 'first stage sampling unit (fsu) code', 'schedule', 'survey year', 'whether urban or rural region', 'nss region, first 2 digits represent state and last one represents sub-region in state; for state codes refer to documentation with opencity or microdata', 'code for district, common integer pool (dist 1 of state 1 coded 1, dist 1 of state 2 coded 1 etc) so combine with state code to create unique district codes', 'stratum', 'sub-stratum', 'subround', 'nss field operations division sub-region', 'serial number of household surveyed', 'level of data, in this case 5', 'serial number of member of the household surveyed', 'age of member', 'start time of activity', 'end time of activity', 'duration of activity in minutes NOT PART OF ORIGINAL DATA calcd using time from and time to vars', 'whether multiple activities performed', 'whether multiple activities performed simultaneously', 'activity code for activity #1', 'activity code for activity #2', 'activity code for activity #3', 'whether activity #1 was major activity among the activities in time slot', 'whether activity #2 was major activity among the activities in time slot', 'whether activity #3 was major activity among the activities in time slot', 'location of activity #1', 'location of activity #2', 'location of activity #3', 'whether payment was given for activity #1', 'whether payment was given for activity #2', 'whether payment was given for activity #3', 'type of enterprise for which activity #1 was performed', 'type of enterprise for which activity #2 was performed', 'type of enterprise for which activity #3 was performed', 'nsc', 'mult']

columndetaillvl5 = pd.DataFrame({'variable_name':shortvarnameslvl5, 'variable_describe':longvarnameslvl5})

print("column details processed")


# %%
# Code to export the dataframes and columndetails

try:
    os.mkdir(filelocation/'Processed TUS 2019 files')
    print('creating folder and saving files...')
    nlevel1.to_csv(filelocation/'Processed TUS 2019 files'/'level1.csv', index=False)
    nlevel2.to_csv(filelocation/'Processed TUS 2019 files'/'level2.csv', index=False)
    nlevel3.to_csv(filelocation/'Processed TUS 2019 files'/'level3.csv', index=False)
    nlevel4.to_csv(filelocation/'Processed TUS 2019 files'/'level4.csv', index=False)
    widenlevel5.to_csv(filelocation/'Processed TUS 2019 files'/'level5.csv', index=False)
    columndetaillvl1.to_csv(filelocation/'Processed TUS 2019 files'/'columndetail_level1.csv', index=False)
    columndetaillvl2.to_csv(filelocation/'Processed TUS 2019 files'/'columndetail_level2.csv', index=False)
    columndetaillvl3.to_csv(filelocation/'Processed TUS 2019 files'/'columndetail_level3.csv', index=False)
    columndetaillvl4.to_csv(filelocation/'Processed TUS 2019 files'/'columndetail_level4.csv', index=False)
    columndetaillvl5.to_csv(filelocation/'Processed TUS 2019 files'/'columndetail_level5.csv', index=False)
    print('all done!')
except PermissionError:
    print('permission denied by system to create folder to save files')
    sys.exit()
except Exception as e:
    print(f'an error occurred while saving output: {e}')
    sys.exit()



