import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import flask
import dash
import os
import pylab as py
import xarray as xr
import pandas as pd
import dash
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd

import numpy as np
import geojsoncontour

def contour_to_geojson(lats_grid, lons_grid, values, n_levels):
    """

    :param lats_grid: Must be in the shape of (n by m)
    :param lons_grid: Must be in the shape of (n by m)
    :param values: must be in the shape of (n by m)
    :return: Returns a geojson for cloropleth plotting
    """
    cs = py.contourf(lons_grid, lats_grid, values)
    geojson = geojsoncontour.contourf_to_geojson(contourf=cs, ndigits=3)
    price_geojson = eval(geojson)

    # Loop through the number of Layers
    arr_temp = np.ones([len(price_geojson["features"]), 2])
    # Create the appropriate structure to store the data
    import pandas as pd
    for i in range(0, len(price_geojson["features"])):
        price_geojson["features"][i]["id"] = i

        # Filling array with price and Id for each geojson spatial object. Z value from contour plot will be stored as title
        arr_temp[i, 0] = i
        arr_temp[i, 1] = float(price_geojson["features"][i]["properties"]["title"][0:4])#.split('-')[0])
    # Transforming array to df
    return pd.DataFrame(arr_temp, columns=["Id", "AirTemperature"]), price_geojson


import os
import xarray as xr
#os.chdir(r'C:\Users\rampaln\OneDrive - NIWA\Research Projects\Test_crop_app\crop-monitoring-app')
df1 = xr.open_dataset(r'MODIS_netcdf.nc')
df1.load()
df = df1['CMG 0.05 Deg Monthly EVI'].isel(time =0)



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
                                 html.H2('MODIS Enhanced Vegetation Index (EVI) Explorer',style={'color': 'k'}),
                                 dcc.Interval(interval=500),
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
                                        dcc.Interval(interval=500),
                                        dcc.Slider(id ="time-slider",min=0, #the first date
                                                       max=len(times)-1, #the last date
                                                       value=len(times)-3,
                                                   tooltip={'always_visible': True}),
                                         html.P('Select a Zoom Level', style={'color': 'k'}),
                                         dcc.Slider(id="zoom-slider", min=3,  # the first date
                                                    max=10,  # the last date
                                                    value=4,
                                                    tooltip={'always_visible': True}),
                                         dcc.Graph(id='funnel-graph'),
                                         dcc.Interval(interval=1000),
                                     ],
                                     style={'color': 'k'})
                                ]
                             ),
                    html.Div(className='six columns',
                             children=[html.H2('Time-Series',style={'color': 'k'}),
                                 html.P('',style={'color': 'k'}),
                                 html.P('',style={'color': 'k'}),
                                 dcc.Graph(id ='funnel-graph2', animate =True),
                                 dcc.Interval(interval=1*500)
                             ])
                              ])
        ])


@app.callback(dash.dependencies.Output('funnel-graph', 'figure'),
              [dash.dependencies.Input('datetimemonth-dropdown', 'value'),
               dash.dependencies.Input("time-slider", "value"),
               dash.dependencies.Input("zoom-slider", "value")])
def update_graph(filename, slider_time, zoom_slider):
    print(slider_time)
    df = df1[filename].isel(time = slider_time)
    time_str = str(pd.to_datetime(df.time.values).date())


    vals = df.values
    lats = df.latitude.values
    lons = df.longitude.values
    Ids, geojson = contour_to_geojson(lats, lons, vals, 10)
    trace2 = go.Choroplethmapbox(
    geojson=geojson,
    locations=Ids.Id,
    z=Ids.AirTemperature,
    colorscale="jet",
    marker_line_width=0,

    marker=dict(opacity=0.5))




    
    lats, lons = np.meshgrid(lats, lons)
    lats = lats.T
    lons = lons.T
    idx = vals > -1.0
    lats2 = lats[idx].ravel()
    lons2 = lons[idx].ravel()
    vals2 = vals[idx].ravel()
    # Note you should only plot these scatter points on the first iteration and then just use them for clicking on the points
    trace1 = go.Scattermapbox(lat=lats2,
                              lon=lons2,
                              mode='markers+text',
                              marker=dict(size=7, showscale=False, color=vals2, colorscale ='rdylgn',cmin=0.01, cmax=0.8, opacity =0.01),
                              textposition='top right',
                              hovertext=[f"{filename} %.2f" % i for i in vals2])
    mapbox = dict(
        center=dict(
            lat=-41,
            lon=175
        ),
        pitch=0,
        zoom=zoom_slider,
        style= "carto-positron")

    # trace2 = go.Bar(x=pv.index, y=pv[('Quantity', 'pending')], name='Pending')
    # trace3 = go.Bar(x=pv.index, y=pv[('Quantity', 'presented')], name='Presented')
    # trace4 = go.Bar(x=pv.index, y=pv[('Quantity', 'won')], name='Won')

    return {
        'data': [trace2, trace1],
        'layout':
            go.Layout(autosize=True, hovermode='closest',
                      title='Average {} on {}'.format(filename.strip("CMG").strip("DEG").strip("Monthly"),time_str),
                      barmode='stack', mapbox=mapbox, height=750, width=800,template= 'seaborn', font=dict(
                family="Courier New, monospace",
                size=10,
            ))
    }


@app.callback(dash.dependencies.Output('funnel-graph', 'value'),
              [dash.dependencies.Input('funnel-graph', 'clickData')])
def update_graph2(foo_click_data):
    print(foo_click_data)
    #foo_click_data = foo_click_data[0]
    return foo_click_data['points'][0]['lat'], foo_click_data['points'][0]['lon']

def demean(a):
    return a - a.sel(time = slice("2002","2020")).mean("time")


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
    trace3 = go.Scatter(x = index, y = [xdata[filename]], mode ='markers+text',name = 'EVI',marker=dict(size=14, color='blue'))
    trace1 = go.Scatter(x=df.index, y=df[filename], name =f'EVI', mode ='lines', textposition = 'bottom center')
    trace2 = go.Scatter(x=df2.index, y=df2[filename], name =f'EVI Anomally', mode='lines', textposition = 'bottom center')
    trace4 = go.Scatter(x=index, y=[xdata2[filename]], mode='markers+text',
                        marker=dict(size=14, color='red'),name = 'EVI Anomally')

    return {
        'data': [trace1, trace2,trace3,trace4],
        'layout':
        go.Layout(
            title='{} Time-Series'.format(filename),#,"%.2f" % lats,"%.2f" % lons),
            barmode='stack', width = 950, height =950,# colorway=["#5E0DAC", '#FF4F00', '#375CB1', '#FF7400', '#FFF400', '#FF0056'],
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


