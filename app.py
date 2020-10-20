# -*- coding: utf-8 -*-
"""
Created on Tue May 26 21:39:12 2020

@author: PaPa
"""

# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from init import *
from const import *

# generate Vietnam's Figure and Phil's figure from init.py
PHILfig, VNfig = genearateFigure(PHIL_HAZARD, PHIL_POLICY, VN_HAZARD, VN_POLICY)

#dash init
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css'] # ref to css style

app = dash.Dash(__name__, external_stylesheets=external_stylesheets) # init dash component
app = dash.Dash(title='GCRF Visualization') # set title
server = app.server # get server variable, this varibale needs to be global varible
app.layout = html.Div(children=[
    html.H1(children='GCRF - Chronological Figure'),
    # add Phil's graph
    dcc.Graph(
        id='P',
        figure=PHILfig
    ),
    # add Vietnamese's graph
    dcc.Graph(
        id='VN',
        figure=VNfig
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)