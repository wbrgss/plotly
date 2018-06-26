# -*- coding: utf-8 -*-

# Dash deps
import dash
import dash_colorscales
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

# Data parsing deps
import json
import pandas as pd
from urllib import urlencode, urlretrieve

import datetime

def fetch_data():
    # Data URI + params
    mparams = {
        'study_id': 16880941,
        'sensor_type': 'gps',
        'max_events_per_individual': 100
    }
    jsonUrl = "https://www.movebank.org/movebank/service/public/json?"
    url = urlencode(mparams, True)
    dat = pd.read_json(jsonUrl + url)
    
    return dat.individuals

app = dash.Dash()

app.css.config.serve_locally=True

app.layout = html.Div([
    html.Link(href='style.css', rel='stylesheet'),
    html.H1('Turkey Vulture Movement Patterns', className='header',
        style={
            'font-family': '"Verdana", Arial, sans-serif',
            'text-align': 'center',
            'color': '#3F007D'
        }
        ),
    html.Div([
        html.Span('Colors', style={
            'font-family': '"Open Sans", Helvetica, Arial, sans-serif',
            'color': '#252525',
            'margin-left': '30px'
        }),
        dash_colorscales.DashColorscales(
            id='color-picker',
            nSwatches=19,
            fixSwatches=True
        )
    ]),
    html.Div(
        [
            dcc.Graph(id='graph'),
            dcc.Interval(
                id='interval-component',
                interval=300*1000,
                n_intervals=0
            )
        ]
    )
], className="map")

@app.callback(
    Output('graph', 'figure'),
    [Input('interval-component', 'n_intervals'),
    Input('color-picker', 'colorscale')],
    [State('graph', 'relayoutData')] 
)
def update_graph(n, colorscale, layout):
    
    birds = fetch_data()

    if layout is not None:
        lon = float(layout['mapbox']['center']['lon'])
        lat = float(layout['mapbox']['center']['lat'])
        zoom = float(layout['mapbox']['zoom'])
    else:
        lon = -76
        lat = 39
        zoom = 4
    fig = {
        'animate': True,
        'layout':  {
            'mapbox': {
                'accesstoken': (
                    'pk.eyJ1Ijoid2JyZ3NzIiwiYSI6ImNqaXY5bGxhdzA2MH' +
                    'gzanFqejdpdGl6ZHEifQ.rwnv9gON_y3ZSM664jZ5rQ'
                ),
                'center': {
                    'lon': lon,
                    'lat': lat
                },
                'style': 'dark',
                'zoom': zoom
            },
            'margin': {
                'l': 0, 'r': 0, 'b': 0, 't': 0
            },
        }
    }

    COLORS = ["#d32f2f", "#d81b60", "#8e24aa", "#5e35b1", "#3949ab", "#1e88e5", \
            "#81d4fa", "#006064", "#00897b", "#4caf50", "#ccff90", "#eeff41", \
            "#ffeb3b", "#ffb300", "#fb8c00", "#ff8a65", "#8d6e63", "#bdbdbd", "#78909c"]

    fig['data'] = [{
        'lat': [l['location_lat'] for l in bird['locations']],
        'lon': [l['location_long'] for l in bird['locations']],
        'type': 'scattermapbox',
        'mode': 'lines',
        'line': {
            'width': 2,
            'color': colorscale[i] if colorscale else COLORS[i]
        },
        'name': bird['individual_local_identifier'],
        'text': [datetime.datetime.fromtimestamp(l['timestamp']/1000) \
                .strftime('%Y-%m-%d %H:%M:%S') for l in bird['locations']]
    } for i, bird in enumerate(birds)]
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True,host='0.0.0.0',port=80)
