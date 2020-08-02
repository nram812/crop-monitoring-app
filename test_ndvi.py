import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import flask
import dash
import os

import xarray as xr
import pandas as pd
import dash
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd

import numpy as np

import os
#os.chdir(r'C:\Users\rampaln\OneDrive - NIWA\Research Projects\Test_crop_app\crop-monitoring-app')
df1 = xr.open_dataset(r'MODIS_netcdf.nc')
#observations = df['CMG 0.05 Deg Monthly NDVI']

server = flask.Flask(__name__)
colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
#app.config.suppress_callback_exceptions = True
#,

# children = [
#     html.Div(
#         id='Username',
#         style={'textAlign': 'center',
#                'verticalAlign': 'middle',
#
#                }

app.layout = html.Div(style={'backgroundColor': colors['background'],'body':0},
    children=[
       html.Div(
                 children=[
                    html.Div(className='six columns',
                             children=[
                                 html.H2('MODIS Satellite Crop Monitoring Tool',style={'color': 'k'}),
                                 html.P('Click on a Location to plot the time-series',style={'color': 'k'}),
                                 html.Div(
                                     className='div-for-dropdown',
                                     children=[
                                         dcc.Dropdown(
                                             id='datetimemonth-dropdown',
                                             options=[{'label': k, 'value': k} for k in list(df1.variables)],
                                             value='CMG 0.05 Deg Monthly EVI',
                                             placeholder="Select Variable",
                                             style=dict(width='40%',
                                                 display='inline-block',
                                                 verticalAlign="middle")),
                                         dcc.Graph(id='funnel-graph', config={'scrollZoom': True,'displayModeBar': True}, animate=True),
                                     ],
                                     style={'color': 'k'})
                                ]
                             ),
                    html.Div(className='six columns',
                             children=[html.H2('Time-Series',style={'color': 'k'}),
                                 html.P('',style={'color': 'k'}),
                                 html.P('',style={'color': 'k'}),
                                 dcc.Graph(id ='funnel-graph2', config={'displayModeBar': True}, animate=True)
                             ])
                              ])
        ])






# app.layout = html.Div([
#     html.H1("New Zealand NDVI and EVI Historical Tool"),
#     html.H3("Select the Dataset (EVI or NDVI)"),
#     dcc.Dropdown(
#         id='datetimemonth-dropdown',
#         options=[{'label': k, 'value': k} for k in list(df1.variables)],
#         value=list(df1.variables)[-2]
#     ),
#
#     html.Hr(),
#     html.H4("Click on Location to Retrieve the data"),
#     # numdate= [x for x in range(len(df['DATE'].unique()))]
#     #
#     # #then in the Slider
#     # dcc.Slider(min=numdate[0], #the first date
#     #                max=numdate[-1], #the last date
#     #                value=numdate[0], #default: the first
#     #                marks = {numd:date.strftime('%d/%m') for numd,date in zip(numdate, df['DATE'].dt.date.unique())})
#     # ])
#     #dcc.RadioItems(id='day-dropdown'),
#     #
#     # html.Hr(),
#     # dcc.Interval(id='auto-stepper',
#     #         interval=1*1000, # in milliseconds
#     #          n_intervals=0),
#     # dcc.Slider(id='utc-dropdown', min = 0, max =step_num,tooltip = { 'always_visible': True }, value =0),
#     html.Div([dcc.Graph(id ='funnel-graph', config={'scrollZoom': True}),
#     dcc.Graph(id ='funnel-graph2')], className= "row"),
# ])


@app.callback(dash.dependencies.Output('funnel-graph', 'figure'),
              [dash.dependencies.Input('datetimemonth-dropdown', 'value')])
def update_graph(filename):
    df = df1[filename].mean("time")

    vals = df.values
    lats = df.latitude.values
    lons = df.longitude.values
    lats, lons = np.meshgrid(lats, lons)
    lats = lats.T
    lons = lons.T
    idx = vals > -1.0
    lats = lats[idx].ravel()
    lons = lons[idx].ravel()
    vals = vals[idx].ravel()
    trace1 = go.Scattermapbox(lat=lats,
                              lon=lons,
                              mode='markers+text',
                              marker=dict(size=7, showscale=True, color=vals, colorscale='ylgn', cmin=vals.min(), cmax=vals.max()),
                              textposition='top right',
                              hovertext=[f"{filename} %.2f" % i for i in vals])
    mapbox = dict(
        center=dict(
            lat=-41,
            lon=175
        ),
        pitch=0,
        zoom=5,
        style="open-street-map")

    # trace2 = go.Bar(x=pv.index, y=pv[('Quantity', 'pending')], name='Pending')
    # trace3 = go.Bar(x=pv.index, y=pv[('Quantity', 'presented')], name='Presented')
    # trace4 = go.Bar(x=pv.index, y=pv[('Quantity', 'won')], name='Won')

    return {
        'data': [trace1],
        'layout':
            go.Layout(autosize=True, hovermode='closest',
                      title='Average {}'.format(filename.strip("CMG").strip("DEG").strip("Monthly")),
                      barmode='stack', mapbox=mapbox, height=800, width=1000,template= 'seaborn')
    }


@app.callback(dash.dependencies.Output('funnel-graph', 'value'),
              [dash.dependencies.Input('funnel-graph', 'clickData')])
def update_graph2(foo_click_data):
    return foo_click_data['points'][0]['lat'], foo_click_data['points'][0]['lon']

def demean(a):
    return a - a.sel(time = slice("1980","2020")).mean("time")


@app.callback(dash.dependencies.Output('funnel-graph2', 'figure'),
              [dash.dependencies.Input('datetimemonth-dropdown', 'value'),
               dash.dependencies.Input('funnel-graph', 'value')])
def update_pre_callback(filename, foo_click_data):
    lats, lons = foo_click_data#pprint.pformat(foo_click_data)['points']['lat'],\
                # pprint.pformat(foo_click_data)['points']['lon']
    delta = 0.05
    df = df1[filename].sel(latitude = slice(lats +delta, lats -delta),
                           longitude = slice(lons-delta, lons+delta)).mean(["latitude","longitude"])
    df2 = df.groupby(df.time.dt.month).apply(demean)
    df2 = df2.to_dataframe()

    df = df.to_dataframe()
    # df2 = df.groupby(df.time.dt.month).apply(demean)
    # df2 = df2.to_dataframe()
    trace1 = go.Scatter(x=df.index, y=df[filename], name =f'{filename} time-series', mode ='lines', textposition = 'bottom center')
    trace2 = go.Scatter(x=df2.index, y=df2[filename], name =f'{filename} deseasonalised anomally series', mode='lines', textposition = 'bottom center')
    return {
        'data': [trace1, trace2],
        'layout':
        go.Layout(
            title='{} Time-Series '.format(filename),
            barmode='stack', width = 1400, height =800,# colorway=["#5E0DAC", '#FF4F00', '#375CB1', '#FF7400', '#FFF400', '#FF0056'],
            template='plotly_white',
            hovermode='x',
            autosize=True,
            plot_bgcolor = 'rgba(0, 0, 0, 0)',
            margin={'t': 50},yaxis=dict(range=[-0.2,0.8]),
        )
    }



if __name__ == '__main__':
    app.run_server(debug=True)


