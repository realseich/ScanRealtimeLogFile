# SCAN LOG FILE tool
# Main input - logfiles
# Output - csv files which are built from processed logfiles
# Path to logfiles directory, selected logfiles names, output csv files directory 
#   are taken from config settings txt file (with json structure inside) scanLogFile_settings_conf_json.txt
# 


import pandas as pd
pd.set_option('display.max_rows', 6)

import warnings
from pandas.errors import SettingWithCopyWarning
warnings.simplefilter(action='ignore', category=(SettingWithCopyWarning))

import os

def percent(row, strat):
    """_Function to calculate percent from .CS.x [B] and .CS.x [S]_
    
    This function calculates percent from two numbers using the formula (Number2 / Number1 - 1) * 100 ,
    rounds it to two decimal places, and convert the result to string with addition of '%' symbol.
    
    Args:
        row (_row from DataFrame_): _description_
        strat (_string_): _value of the Strategy.Limit_

    Returns:
        _row for DataFrame_: _description_
    """
    
    try:
        if row[strat + ' [S]'][1] != 0:
            row[strat] = str(round((row[strat + ' [S]'][1] / row[strat + ' [B]'][1] - 1) * 100, 2)) + '%'
        else:
            row[strat] = None
    except:
        row[strat] = None
    finally:
        return row
      

def back_to_at(row, strat_lims_ords):
    """_function to transform [Quantity, Price] back to Quantity@Price_
    
    This function transforms list of ['Quantity', 'Price'] to string like 'Quantity@Price'
    
    Args:
        row (_row from DataFrame_): _description_
        strat_lims_ords (_string_): _value of the <Strategy.Limit [Order]>_

    Returns:
        _row for DataFrame_: _description_
    """
    
    try:
        row[strat_lims_ords] = str(row[strat_lims_ords][0]) + '@' + str(row[strat_lims_ords][1]).replace('.',',')
    except:
        row[strat_lims_ords] = None
    finally:
        return row

    
def dir_filename_correct(row):
    """_function to correct dirs and file names_

    This function removes starting and ending spaces of the names and add '/' to end of dir names if doesn't exists
    (and add .log extension to the logfile names if not present)
    
    Args:
        row (_row of the DataFrame_): _description_

    Returns:
        _row of the DataFrame_: _description_
    """
    
    row['Path to directory which contains log files'] = row['Path to directory which contains log files'].strip()
    row['Path to directory where output files will be created'] = row['Path to directory where output files will be created'].strip()
    row['Names of the logfiles to be scanned'] = row['Names of the logfiles to be scanned'].strip()
    if row['Path to directory which contains log files'][-1] != '/':
        row['Path to directory which contains log files'] = row['Path to directory which contains log files'] + '/'
    if row['Path to directory where output files will be created'][-1] != '/':
        row['Path to directory where output files will be created'] = row['Path to directory where output files will be created'] + '/'
    #if row['Names of the logfiles to be scanned'][-4:] != '.log':
        #row['Names of the logfiles to be scanned'] = row['Names of the logfiles to be scanned'] + '.log'
    return row


#---------------------------------------------------------------------------------------------------------
# constants and variables definition
#
strats_lims = ['.XTR.CS.1', '.XTR.CS.2', '.XTR.CS.3', '.XTR.CS.4', '.XTR.CS.5', '.XTR.CS.6'] 
  # definition of startegies.limits which are in the scope
orders = ['[B]', '[S]']   # definition of actions
strats_lims_ords = []   # combinations of startegies.limits and actions


#---------------------------------------------------------------------------------------------------------
# building the strats_lims_ords (combinations of startegies.limits and actions)
#
for i in orders:
    for j in strats_lims:
        strats_lims_ords.append(j + ' ' + i)
strats_lims_ords_b = strats_lims_ords[:int(len(strats_lims_ords)/2)]
strats_lims_ords_b.reverse()
strats_lims_ords_s = strats_lims_ords[int(len(strats_lims_ords)/2):]
strats_lims_ords = strats_lims_ords_b + strats_lims_ords_s



#---------------------------------------------------------------------------------------------------------
# Main function which processes logfiles and build output files
#

def one_log_treatment(log_dir, output_dir, log_name):
    """_one logfile treatment_

    This function does all processimng for one logfile.
    
    Args:
        log_dir (_string_): _Name of the directory which contains logfile_
        output_dir (_string_): _Name of the directory for output file_
        log_name (_string_): _Name of the logfile_
        last (boolean): _if it the the last logfile to be processed
    """

    print(pd.Timestamp.now().round(freq='s'), '- Proceeding with logfile', log_name)

    #-------------------------------------------------------------------------------------------------------------------
    # Check if the directories and logfile, specified in the settings file, exist
    #
    
    try:
        logfiles_dir = os.listdir(log_dir)
    except FileNotFoundError:
        print(pd.Timestamp.now().round(freq='s'), '- !!! Directory', log_dir, "," \
            '\n                      specified in the settings file as a path to logfile', log_name, "," \
                '\n                      does not exist. !!!')
        return
    
    try:
        otputfiles_dir = os.listdir(output_dir)
    except FileNotFoundError:
        print(pd.Timestamp.now().round(freq='s'), '- !!! Directory', output_dir, "," \
            '\n                      specified in the settings file as a path to output file for logfile', log_name, "," \
                '\n                      does not exist. !!!')
        return
    
    files_list = os.listdir(log_dir)
    if log_name not in files_list:
        print(pd.Timestamp.now().round(freq='s'), '- !!! Logfile', log_name, \
            ', specified in the settings file, does not exist. !!!')
        return

     
    #-------------------------------------------------------------------------------------------------------------------
    # logfile opening
    #
    
    try:
        with open(log_dir + log_name, 'r') as logfile:
            log = pd.read_table(logfile, index_col=None, names=range(0,20), low_memory=False)
    except:
        print(pd.Timestamp.now().round(freq='s'), '- !!! Logfile', log_name, 'can not be processed. !!! \
            \nAsk the code developer to investigate and fix the issue.')
        return


    #---------------------------------------------------------------------------------------------
    # log with required combinations of startegies.limits and actions only
    #
    log_strats_lims_ords = log[log[3].str[12:].isin(strats_lims_ords)]  


    #------------------------------------------------------------------------------------
    # to correct the columns issue in CANCEL (C:CNL) rows (introduced while pd.read_table)
    #
    # splitting the table in ADD/CHANGE and CANCEL parts in order to correct the columns issue in CANCEL rows (introduced while pd.read_table):
    #
    add_chg = log_strats_lims_ords[(log_strats_lims_ords[2] == 'C:ADD') | (log_strats_lims_ords[2] == 'C:CHG')]
    cnl = log_strats_lims_ords[log_strats_lims_ords[2] == 'C:CNL']
    #
    # restructure CNL part:
    #
    cnl.drop(axis=1, labels=[18,19], inplace=True)
    cnl.rename(columns={8:10,9:11,10:12,11:13,12:14,13:15,14:16,15:17,16:18,17:19}, inplace=True) 
    cnl.insert(8, column=8, value=None)
    cnl.insert(9, column=9, value=None)
    #
    # combine ADD/CHANGE and CANCEL again in one table:
    #
    log_strats_lims_ords = pd.concat([add_chg, cnl], axis=0, ignore_index=False)
    log_strats_lims_ords.sort_index(axis=0, ascending=True, inplace=True, kind='stable', ignore_index=False)


    #------------------------------------------------------------------------------------
    # transform Quantity@Price to [Quantity, Price] list
    #
    log_strats_lims_ords[4] = log_strats_lims_ords[4].apply(lambda x: str(x).split('@'))
    log_strats_lims_ords[4] = log_strats_lims_ords[4].apply(lambda x: [x[0],float(x[1].replace(',', '.'))])


    #------------------------------------------------------------------------------------
    # build the list of ISINs in the scope of the log
    #
    isin_list = log_strats_lims_ords[3].str[:12].unique()   # list of ISINs in the scope of the log


    #------------------------------------------------------------------------------------
    # build a dict where keys are ISINs and values are part of the log for specific ISIN
    #
    log_split_by_isin = {}  # dictinary which contains individual log per each ISIN (keys=ISINs)
    for isin in isin_list:
        log_split_by_isin[isin] = log_strats_lims_ords[log_strats_lims_ords[3].str[:12] == isin]


    #------------------------------------------------------------------------------------
    # dictinary which will contain individual output per each ISIN (keys=ISINs, values - output table per specific ISIN)
    #
    isin_output = {}  # dictinary which will contain individual output per each ISIN (keys=ISINs)  


    #------------------------------------------------------------------------------------
    # bulid an output table from logfile for each ISIN
    #
    for isin in log_split_by_isin: 
        
        isin_split_by_stratLimAct = {}  
            # dictinary which contains the individual log per each combinations of startegies.limits and actions (for ISIN)
        for strat in strats_lims_ords:
            isin_split_by_stratLimAct[strat] = log_split_by_isin[isin][log_split_by_isin[isin][3].str[12:] == strat]
            
        stratLimAct_output = {}  
            # dictinary which will contain the individual output per each combinations of startegies.limits and actions (for ISIN)
        for strat in isin_split_by_stratLimAct:
            stratLimAct_output[strat] = isin_split_by_stratLimAct[strat][[3,0,2,14,4]]
            stratLimAct_output[strat].rename(columns={3:'ISIN',0:'Timestamp',2:'Action',14:'Phase',4:strat}, inplace=True) 
            stratLimAct_output[strat]['ISIN'] = stratLimAct_output[strat]['ISIN'].str[:12]
            stratLimAct_output[strat].insert(1, column='Strategy', value=strat)
            
        isin_output[isin] = pd.DataFrame(columns = ['ISIN','Strategy','Timestamp','Action','Phase']) 
            # empty table for ISIN with common column names
        
        # combine vertically individual outputs per each combinations of startegies.limits and actions in a common output (for ISIN):
        for strat in stratLimAct_output.keys():
            isin_output[isin] = isin_output[isin].merge(stratLimAct_output[strat], how='outer')
        isin_output[isin].sort_values(by='Timestamp', axis=0, ascending=True, kind='stable', ignore_index=True, inplace=True)
            # sort common output by timestamp
        
        # propogate [Quantity, Price] to the following empty cells up to ClosingAuction:
        for strat in strats_lims_ords:
            isin_output[isin][strat].fillna(inplace=True,method='ffill')    # propogate [Quantity, Price] to the following empty cells
            close_auction = isin_output[isin][(isin_output[isin]['Phase'] == 'Phase=ClosingAuction') \
                & (isin_output[isin]['Strategy'] == strat)].last_valid_index()
                    # detrmine the index of ClosingAuction row
            
            if close_auction != None:   
                # only for >Strategies.Limits [Orders]< for ehich auction was closed:
                isin_output[isin][strat][close_auction+1::] = None  
                    # set to Null [Quantity, Price] cells after ClosingAuction (them were filled by previous values by ffill method above)
        
        # calculate the percentage from .CS.x [B] and .CS.x [S]:
        for strat in strats_lims:
            isin_output[isin][strat] = None
            isin_output[isin] = isin_output[isin].apply(lambda row: percent(row, strat), axis=1)
        
        #transform [Quantity, Price] back to Quantity@Price:
        for strat in strats_lims_ords:
            isin_output[isin] = isin_output[isin].apply(lambda row: back_to_at(row, strat), axis=1)

    #-----------------------------------------------------------------------------------------------------------------------
    # combine vertically individual outputs per each combinations of startegies.limits and actions in a common output (for ISIN)
    #
    all_isins_output = pd.DataFrame(columns=isin_output[isin_list[0]].columns) # columns structure for common output table
    #
    # combine vertically output tables for all ISINs:
    for isin in isin_list:
        all_isins_output = pd.concat([all_isins_output, isin_output[isin]], axis=0, ignore_index=True)



    #-----------------------------------------------------------------------------------------------------------------------
    # create an output file for ISIN:
    #
    output_file_path_name = output_dir + log_name[:-4] + '_output.csv'      # build the path/name of output csv file
    
    try:
        all_isins_output.to_csv(output_file_path_name, index=False, sep=',')
        print(pd.Timestamp.now().round(freq='s'), '- Output csv file for logfile', log_name, 'created.')
    except PermissionError:
        print(pd.Timestamp.now().round(freq='s'), '- !!! Output csv file (', output_file_path_name, \
            ')\n                      for logfile', log_name, \
                '\n                       already exists and can not be overwritten. !!!')
        
        

#---------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------
# Main code block - reads settings file and calls main fuction to procees logfiles
#

#-------------------------------------------------------------------------------------------------------------------
# settings file opening and saving as DataFrame
#

try:
    with open('scanLogFile_settings_conf_json.txt', 'r') as setfile:
        settings = setfile.read()
except FileNotFoundError:
    print(pd.Timestamp.now().round(freq='s'), '- !!! Settings file is not present in the same directory as this exe file.\nProgram is STOPPED. !!!')
    os.system("pause")

settings = settings.replace('\\','/')

try:
    settings = pd.read_json(settings)
except:
    print(pd.Timestamp.now().round(freq='s'), '- !!! The settings file (scanLogFile_settings_conf.json) has a wrong structure and can not be interpreted. \
        \n                      Program is STOPPED. !!!')
    os.system("pause")


#---------------------------------------------------------------------------------------------------------------
# remove the spaces in the begining and the end of the directories and logfiles names
# and add '/' to the end of the directories names if not provided
# (and add .log extension to the logfile names if not present)
# 
settings = settings.apply(lambda row: dir_filename_correct(row), axis=1)


#---------------------------------------------------------------------------------------------------------------
# run the script over logfiles
# 
for i in settings.index:
    
    try:
        one_log_treatment(settings.loc[i]['Path to directory which contains log files'] \
            , settings.loc[i]['Path to directory where output files will be created'] \
            , settings.loc[i]['Names of the logfiles to be scanned'])
    except:
        pass
    
    if i == settings.index[-1]:
        print(pd.Timestamp.now().round(freq='s'), '- It was the last logfile in the list. Program is FINISHED.')
    
os.system("pause") # to keep the window opened


# The END
