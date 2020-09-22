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


PHILfig, VNfig = genearateFigure(PHIL_HAZARD, PHIL_POLICY, VN_HAZARD, VN_POLICY)

#dash init
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app = dash.Dash(title='GCRF Visualization')
server = app.server
app.layout = html.Div(children=[
    html.H1(children='GCRF - Chronological Figure'),
    dcc.Graph(
        id='P',
        figure=PHILfig
    ),
    dcc.Graph(
        id='VN',
        figure=VNfig
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
