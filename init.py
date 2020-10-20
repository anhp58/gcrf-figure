# -*- coding: utf-8 -*-
"""
Created on Tue May 26 21:39:12 2020

@author: PaPa
"""

# -*- coding: utf-8 -*-

import plotly.graph_objects as go 
import pandas as pd
import numpy as np
from const import *

#from datetime import datetime

def changeSymbol():
    """Get the symbol list to generate the event for the figure
        Args:
            None
        Returns:
            symbol list (arr): 12 symbols
    """
    #old version using default order of symbol list
# =============================================================================
#     from plotly.validators.scatter.marker import SymbolValidator
#     
#     raw_symbols = SymbolValidator().values
#     symbol_list_with_open_dot =  [raw_symbols[i] for i in range (1, len(raw_symbols), 2)]
#     
#     return [symbol_list_with_open_dot[i] for i in range (24, len(symbol_list_with_open_dot), 4)]
# =============================================================================
    #new version, predefine the symbol list
    return ['circle', 'square', 'diamond', 'cross', 'x', 'triangle', 'pentagon', \
            'hexagram', 'star', 'diamond', 'hourglass', 'bowtie']

def readExcel(xls_path):
    """Read the excel file
        Args: 
            xls_path (string)
        Returns: xlsx object and list sheet' name
    """
    print(f'Loading {xls_path} into pandas')
    xl = pd.ExcelFile(xls_path)
    names = xl.sheet_names
    
    return xl, names

def naToNone (df):
    """Replace na to 0
        Args:
            df (dataframe): input dataframe
        Returns:
            df (dataframe): removed na value dataframe
    """
    return df.replace('na', np.nan)

def normalizeData(inarr):
    """Normalize data value to same range
        Args:
            inarr (arr): input array which needs to be normalized
        Returns:
            normalized array (arr)
    """
    return (inarr - min(inarr) + 1e-8) / (max(inarr) + 1e-8 - min(inarr))

def sortByTime (time_list, unsort_list):
    """Sort one list by the order of the other
        Args:
            time_list (list): time list that needs to be sorted for the x axe of the figure
            unsort_list (list): the value list that needs to be sorted by the time list
        Returns:
            sorted lists (list)

    """
    return [x for _,x in sorted(zip(time_list,unsort_list))]

def stringToDate (string_arrr):
    """Date interpreting from the raw input value
        Args:
            string_arrr (list): raw input value
        Returns:
            final (list): corrected date with four digits
    """
    
    final = []
    for timestr in string_arrr:

        timestr = "0"*(6 - len(str(timestr))) + str(timestr)
        #convert year from 2 numbers to 4 numbers
        if int(timestr[-2:]) <= 20:
            year = str(int(timestr[-2:]) + 2000)
        else:
            year = str(int(timestr[-2:]) + 1900)
        # final.append(datetime.strptime(timestr[2:4] + " " + year, '%m %Y')) #concat month and year
        final.append(int(year))
        # final.append(datetime.strptime(year, '%Y'))
    return final

def MagnitudeDataCooking (xl, names, magnitude_field, time_field, symbol_list, index, jump_step, drop_index):
    """Create the Magnitude data for the figure visualization
        Args:
            xl (object): xl object, collected from readExcel
            names (list): list of sheet' name of an excel file
            magnitude_field (string): magnitue criteria - a column in a sheet
            time_field (string): string value of the time field in a sheet
            symbol_list (list): symbol list collected from changeSymbol()
            index (int): initiation axe's value for an event
            jump_step (int): the distance of two lines in the figure
            drop_index (int): the number of columns that we drop when loop through the file
        Returns:
            figure_data_list (dict) contains:
                                    x axe: year list
                                    y axe: same value for all records of an event
                                    marker_size: value for each symbol size
                                    name: event name
                                    marker_symbol: symbol of an event
    """
    
    figure_data_list = []
    i = index
    for name, symbol in zip(names[:-drop_index], symbol_list): #drop drop_index column

        i = i+ jump_step # the jump step
        result_dictionary = {}
        event = naToNone(xl.parse(name))
        
        fine_date_list = stringToDate(event[time_field])
        fine_mag_list =  normalizeData(event[magnitude_field].fillna(0))
        
        result_dictionary['x'] = sorted(fine_date_list)
        result_dictionary['y'] = np.full(len(sorted(stringToDate(event[time_field]))), i)
        result_dictionary['marker_size'] = sortByTime(fine_date_list, fine_mag_list*BUBBLE_SIZE)
        result_dictionary['name'] = "{} of {}".format(magnitude_field, name)
        result_dictionary['marker_symbol'] = symbol
        figure_data_list.append(result_dictionary)

    return figure_data_list


def FrequencyDataCooking (xl, names, time_field, mode, symbol_list, prefix_name_label, index, jump_step):
    """Creates the Frequency data for the figure visualization
        Args:
            xl (object): xl object, collected from readExcel
            names (list): list of sheet' name of an excel file
            time_field (string): string value of the time field in a sheet
            mode (string): 'normal' for hazard event frequency, 'rank' for policy relevance
            symbol_list (list): symbol list collected from changeSymbol()
            prefix_name_model (string): prefix for name of an event
            index (int): initiation axe's value for an event
            jump_step (int): the distance of two lines in the figure
        Returns:
            figure_data_list (dict) contains:
                                            x axe: year list
                                            y axe: same value for all records of an envent
                                            marker_size: value for each symbol size
                                            name: event name
                                            marker_symbol: symbol of an event
    """
    
    figure_data_list = []
    i = index
    
    for name, symbol in zip(names, symbol_list):
        i = i + jump_step#the jump step
        result_dictionary = {}
        event = xl.parse(name)
        
        event_date = stringToDate(event[time_field].values.tolist())
        distinct_event_date_list = set(event_date)
        
        temp = []
        for date in sorted(distinct_event_date_list):
            if mode == FREQUENCY_MODE[1]: # mode = rank for policy 
                # 1 and 2 need to be removed when do the sum calculation for policy ranking within a year
                temp.append(event[event[time_field] == date]['Rank'].replace(1, 0).replace(2, 0).sum())
            else:
                temp.append(event_date.count(date))
        # print (distinct_event_date_list)
        result_dictionary['x'] = sorted(distinct_event_date_list)
        result_dictionary['y'] = np.full(len(result_dictionary['x']), i)
        result_dictionary['marker_size'] = normalizeData(np.array(temp))*BUBBLE_SIZE
        result_dictionary['name'] = "{} {}".format(name, prefix_name_label)
        result_dictionary['marker_symbol'] = symbol
        figure_data_list.append(result_dictionary)
    return figure_data_list
    
def TimeMagnitudeFigure (figure_data_list, title):
    """Generate figure from list of dictionaries
        Args:
            figure_data_list
            title
        Returns:
            fig ()
    """
    
    fig = go.Figure()
    bubble_list = []
    
    for figure_dict in figure_data_list:

        bubble_list.append(go.Scatter(
            x = figure_dict['x'], 
            y = figure_dict['y'],
            mode='lines+markers',
            marker_size = figure_dict['marker_size'],
            marker_symbol = figure_dict['marker_symbol'],
            name = figure_dict['name'])
        )

    fig = go.Figure(data=bubble_list)
    fig.update_layout(
        title=title,
        xaxis_title="Year",
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="#7f7f7f"
        )
    )
    fig.update_yaxes(showticklabels=False) # to turn of the Y label
    return fig

def genearateFigure(PHILhazard, PHILpolicy, VNhazard, VNpolicy):
    """Generates two figures from 01 phil hazard excel file, 01 phil policy excel file, 
        01 vietnam hazard db, 01 vietnam policy db
        Args:
            PHILhazard (string): Phillipines Hazard DB - xlsx path
            PHILpolicy (string): Phillipines Policy DB - xlsx path
            VNhazard (string):  Vietnam Hazard DB - xlsx path
            VNpolicy (string): Vietnam Policy DB - xlsx path
        Returns:
            PHILfig (dict): Phillipines figure
            VNfig (dict): Vietnam figure
    """
    symbol_list = changeSymbol()
    #Philippines hazards
    xl, names = readExcel(PHILhazard)
    phil_ppl_affected_list = MagnitudeDataCooking (xl, names, MAGNTITUDE_FIELD[0], TIME_FIELD[0], \
                                                          symbol_list, index=1, jump_step=15, drop_index=1)
        
    phil_facilities_list = MagnitudeDataCooking (xl, names, MAGNTITUDE_FIELD[1], TIME_FIELD[0], \
                                                        symbol_list, index=4, jump_step=15, drop_index=1)
        
    phil_occurence_dict_list = FrequencyDataCooking(xl, names, TIME_FIELD[0],FREQUENCY_MODE[0], symbol_list, \
                                                        FREQUENCY_PREFIX_LABEL[0], index=7, jump_step=15)
    
    #Philippines policy
    xl, names = readExcel(PHILpolicy)
    phil_policy_rank_dict_list = FrequencyDataCooking(xl, names, TIME_FIELD[1], FREQUENCY_MODE[1], symbol_list, \
                                                        FREQUENCY_PREFIX_LABEL[1], index=70, jump_step=3)
    
    #aggreate figure for Phil DB
    phil_db = phil_ppl_affected_list + phil_facilities_list+ phil_occurence_dict_list + phil_policy_rank_dict_list
    PHILfig = TimeMagnitudeFigure (phil_db, "Philippines Database - Hazards and Policies")
    
    #Vietnamese Policy
    xl, names = readExcel(VNpolicy)
    vn_policy_mag_dict_list = FrequencyDataCooking(xl, names, TIME_FIELD[1], FREQUENCY_MODE[1], symbol_list, \
                                                    FREQUENCY_PREFIX_LABEL[1], index=70, jump_step=15)
    #Vietnames hazard
    xl, names = readExcel(VNhazard)
    vn_facilities_list = MagnitudeDataCooking (xl, names, MAGNTITUDE_FIELD[1], TIME_FIELD[0], symbol_list, \
                                                      index=1, jump_step=15, drop_index=2)
    
    vn_occurence_dict_list = FrequencyDataCooking(xl, names, TIME_FIELD[0], FREQUENCY_MODE[0], symbol_list, \
                                                    FREQUENCY_PREFIX_LABEL[0], index=7, jump_step=15)
    
    vn_db = vn_facilities_list+ vn_occurence_dict_list + vn_policy_mag_dict_list
    VNfig = TimeMagnitudeFigure (vn_db, "Vietnam Database - Hazards and Policies")
    
    return PHILfig, VNfig