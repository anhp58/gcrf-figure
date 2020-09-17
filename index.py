# -*- coding: utf-8 -*-
"""
Created on Tue May 26 21:39:12 2020

@author: PaPa
"""

# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from app import server
import plotly.graph_objects as go 

import pandas as pd
from datetime import datetime
import numpy as np

import os

BUBBLE_SIZE = 30
PHIL_LINE = 0
VN_LINE = 0

def changeSymbol():
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
    return ['circle', 'square', 'diamond', 'cross', 'x', 'triangle', 'pentagon', 'hexagram', 
            'star', 'diamond', 'hourglass', 'bowtie']

def read_excel_sheets(xls_path):
    print(f'Loading {xls_path} into pandas')
    xl = pd.ExcelFile(xls_path)
    names = xl.sheet_names
    
    return xl, names

def naToNone (df):
    return df.replace('na', np.nan)

def normalizeData(inarr):
    return (inarr - min(inarr) + 1e-8) / (max(inarr) + 1e-8 - min(inarr))

def sortByTime (time_list, unsort_list):
    return [x for _,x in sorted(zip(time_list,unsort_list))]

def stringToDate (string_arrr):
    
    final = []
    for timestr in string_arrr:

        timestr = "0"*(6 - len(str(timestr))) + str(timestr)
        #convert year from 2 numbers to 4 numbers
        if int(timestr[-2:]) < 20:
            year = str(int(timestr[-2:]) + 2000)
        else:
            year = str(int(timestr[-2:]) + 1900)
        # final.append(datetime.strptime(timestr[2:4] + " " + year, '%m %Y')) #concat month and year
            final.append(int(year))
        # final.append(datetime.strptime(year, '%Y'))
    return final

def MagnitudeDataCooking (xl, names, magnitude_field, time_field, symbol_list):
    
    figure_data_list = []
    i = 0
    for name, symbol in zip(names[:-1], symbol_list): #drop Meteorology column
        # print (name)
        i = i+ 3
        result_dictionary = {}
        event = naToNone(xl.parse(name))
        
        result_dictionary['x'] = sorted(stringToDate(event[time_field]))
        result_dictionary['y'] = np.full(len(sorted(stringToDate(event[time_field]))), i)
        result_dictionary['marker_size'] = sortByTime(sorted(stringToDate(event[time_field])), 
                                   normalizeData(event[magnitude_field].fillna(0))*BUBBLE_SIZE)
        result_dictionary['name'] = "{} of {}".format(magnitude_field, name)
        result_dictionary['marker_symbol'] = symbol
        figure_data_list.append(result_dictionary)
    return figure_data_list, i


def OccurenceDataCooking (xl, names, time_field, index, mode, symbol_list):
    
    
    figure_data_list = []
    i = index
    
    for name, symbol in zip(names, symbol_list):
        i = i+3
        result_dictionary = {}
        event = xl.parse(name)
        
        event_date = stringToDate(event[time_field].values.tolist())
        distinct_event_date_list = set(event_date)
        
        temp = []
        for date in distinct_event_date_list:
            if mode == 'rank':
                temp.append(event[event[time_field] == date]['Rank'].replace(1, 0).replace(2, 0).replace(3, 0).sum())
            else:
                temp.append(event_date.count(date))
        # print (distinct_event_date_list)
        # print (temp)
        result_dictionary['x'] = sorted(distinct_event_date_list)
        result_dictionary['y'] = np.full(len(result_dictionary['x']), i)
        result_dictionary['marker_size'] = sortByTime(result_dictionary['x'], 
                                                      normalizeData(np.array(temp))*BUBBLE_SIZE)
        result_dictionary['name'] = "Occurence_{}".format(name)
        result_dictionary['marker_symbol'] = symbol
        figure_data_list.append(result_dictionary)
    return figure_data_list
    
def TimeMagnitudeFigure (figure_data_list, title):
    
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
        yaxis_title=" ",
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="#7f7f7f"
        )
    )
    return fig


def dash_call (PHILfig, VNfig):
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
    app.layout = html.Div(children=[
        html.H1(children='GCRF - Chronological Figure'),

        # html.Div(children='''
        #     Dash: A web application framework for Python.
        # '''),

        dcc.Graph(
            id='P',
            figure=PHILfig
        ),
        dcc.Graph(
            id='VN',
            figure=VNfig
        )
    ])
    return app

if __name__ == '__main__':
    
    PHILhazard = "./data/Phil_DB.xlsx"
    VNhazard = "./data/VN_DB.xlsx"
    VNpolicy = "./data/VN_policy.xlsx"
    
    symbol_list = changeSymbol()
    
    xl, names = read_excel_sheets(PHILhazard)  
    mag_dict_list, index = MagnitudeDataCooking (xl, names, 'People affected', 'Date', symbol_list)
    occurence_dict_list = OccurenceDataCooking(xl, names, 'Date', index, "", symbol_list)   
    phil_db = mag_dict_list + occurence_dict_list
    PHILfig = TimeMagnitudeFigure (phil_db, "Philippines Database - Time and Magnitude of Events")
    
    xl, names = read_excel_sheets(VNpolicy)
    policy_mag_dict_list = OccurenceDataCooking(xl, names, 'Year', 0, "rank", symbol_list)
    
    xl, names = read_excel_sheets(VNhazard)
    occurence_dict_list = OccurenceDataCooking(xl, names, 'Date', 8, "", symbol_list)
    vn_db = occurence_dict_list + policy_mag_dict_list
    VNfig = TimeMagnitudeFigure (vn_db, "Vietnam Database - Time, Occurence of Events and Policy")
    
    app = dash_call (PHILfig, VNfig)
    server = app.server
    app.run_server(debug=True)