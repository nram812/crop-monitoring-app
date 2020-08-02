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
df1.load()
#observations = df['CMG 0.05 Deg Monthly NDVI']

server = flask.Flask(__name__)
colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}
server = flask.Flask(__name__)
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, server = server)
#app.config.suppress_callback_exceptions = True
#,

# children = [
#     html.Div(
#         id='Username',
#         style={'textAlign': 'center',
#                'verticalAlign': 'middle',
#
times = df1.time.to_index()

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
                                             options=[{'label': k, 'value': k} for k in ['CMG 0.05 Deg Monthly EVI']],
                                             value='CMG 0.05 Deg Monthly EVI',
                                             placeholder="Select Variable",
                                             style=dict(width='40%',
                                                 display='inline-block',
                                                 verticalAlign="middle")),
                                        dcc.Slider(id ="time-slider",min=0, #the first date
                                                       max=len(times)-1, #the last date
                                                       value=0,
                                                   tooltip={'always_visible': True}),
                                         dcc.Interval(interval=500),
                                         dcc.Graph(id='funnel-graph'),
                                     ],
                                     style={'color': 'k'})
                                ]
                             ),
                    dcc.Interval(interval=1 * 1),
                    html.Div(className='six columns',
                             children=[html.H2('Time-Series',style={'color': 'k'}),
                                 html.P('',style={'color': 'k'}),
                                 html.P('',style={'color': 'k'}),
                                 dcc.Interval(interval=1*100),
                                 dcc.Graph(id ='funnel-graph2'),
                                 dcc.Interval(interval=1*100)
                             ])
                              ])
        ])


@app.callback(dash.dependencies.Output('funnel-graph', 'figure'),
              [dash.dependencies.Input('datetimemonth-dropdown', 'value'),
               dash.dependencies.Input("time-slider", "value")])
def update_graph(filename, slider_time):
    print(slider_time)
    df = df1[filename].isel(time = slider_time)
    time_str = str(pd.to_datetime(df.time.values).date())


    vals = df.values
    lats = df.latitude.values
    lons = df.longitude.values
    lats, lons = np.meshgrid(lats, lons)
    lats = lats.T
    lons = lons.T
    idx = vals > -1.0
    lats2 = lats[idx].ravel()
    lons2 = lons[idx].ravel()
    vals2 = vals[idx].ravel()
    trace1 = go.Scattermapbox(lat=lats2,
                              lon=lons2,
                              mode='markers+text',
                              marker=dict(size=7, showscale=True, color=vals2, colorscale ='rdylgn',cmin=-0.3, cmax=0.8),
                              textposition='top right',
                              hovertext=[f"{filename} %.2f" % i for i in vals2])
    mapbox = dict(
        center=dict(
            lat=-41,
            lon=175
        ),
        pitch=0,
        zoom=4,
        style="open-street-map")

    # trace2 = go.Bar(x=pv.index, y=pv[('Quantity', 'pending')], name='Pending')
    # trace3 = go.Bar(x=pv.index, y=pv[('Quantity', 'presented')], name='Presented')
    # trace4 = go.Bar(x=pv.index, y=pv[('Quantity', 'won')], name='Won')

    return {
        'data': [trace1],
        'layout':
            go.Layout(autosize=True, hovermode='closest',
                      title='Average {} on {}'.format(filename.strip("CMG").strip("DEG").strip("Monthly"),time_str),
                      barmode='stack', mapbox=mapbox, height=700, width=700,template= 'seaborn', font=dict(
                family="Courier New, monospace",
                size=10,
            ))
    }


@app.callback(dash.dependencies.Output('funnel-graph', 'value'),
              [dash.dependencies.Input('funnel-graph', 'clickData')])
def update_graph2(foo_click_data):
    return foo_click_data['points'][0]['lat'], foo_click_data['points'][0]['lon']

def demean(a):
    return a - a.sel(time = slice("1980","2020")).mean("time")


@app.callback(dash.dependencies.Output('funnel-graph2', 'figure'),
              [dash.dependencies.Input('datetimemonth-dropdown', 'value'),
               dash.dependencies.Input('funnel-graph', 'value'),
               dash.dependencies.Input("time-slider", "value")])
def update_pre_callback(filename, foo_click_data,time_slider):
    delta = 0.05
    try:
        lats, lons = foo_click_data#pprint.pformat(foo_click_data)['points']['lat'],\

                # pprint.pformat(foo_click_data)['points']['lon']
    except TypeError:
        lats = -38.5
        lons = 176.5 # Choosing a random location
    value_data = df1['CMG 0.05 Deg Monthly EVI'].isel(time=time_slider).sel(latitude = slice(lats +delta, lats -delta),
                           longitude = slice(lons-delta, lons+delta)).mean(["latitude","longitude"])
    time_value = pd.to_datetime(value_data.time.values)


    df = df1[filename].sel(latitude = slice(lats +delta, lats -delta),
                           longitude = slice(lons-delta, lons+delta)).mean(["latitude","longitude"])
    df2 = df.groupby(df.time.dt.month).apply(demean)
    df2 = df2.to_dataframe()

    df = df.to_dataframe()
    xdata = df.loc[time_value]
    index = df.index.intersection([time_value])
    xdata2 = df2.loc[time_value]
    # df2 = df.groupby(df.time.dt.month).apply(demean)
    # df2 = df2.to_dataframe()
    trace3 = go.Scatter(x = index, y = [xdata[filename]], mode ='markers+text',name = 'NDVI',marker=dict(size=14, color='blue'))
    trace1 = go.Scatter(x=df.index, y=df[filename], name =f'{filename} time-series', mode ='lines', textposition = 'bottom center')
    trace2 = go.Scatter(x=df2.index, y=df2[filename], name =f'{filename} deseasonalised anomally series', mode='lines', textposition = 'bottom center')
    trace4 = go.Scatter(x=index, y=[xdata2[filename]], mode='markers+text',
                        marker=dict(size=14, color='red'),name = 'NDVI Anomally')

    return {
        'data': [trace1, trace2,trace3,trace4],
        'layout':
        go.Layout(
            title='{} Time-Series Lat:{} Lon:{}'.format(filename,"%.2f" % lats,"%.2f" % lons),
            barmode='stack', width = 900, height =600,# colorway=["#5E0DAC", '#FF4F00', '#375CB1', '#FF7400', '#FFF400', '#FF0056'],
            template='plotly_white',
            hovermode='x',
            autosize=True,
            font=dict(
                family="Courier New, monospace",
                size=10,
            ),
            plot_bgcolor = 'rgba(0, 0, 0, 0)',
            margin={'t': 100},yaxis=dict(range=[-0.2,0.8]),
        )
    }



if __name__ == '__main__':
    app.run_server(debug=True)


