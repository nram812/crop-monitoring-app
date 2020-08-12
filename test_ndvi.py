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
import xarray as xr
os.chdir(r'C:\Users\rampaln\OneDrive - NIWA\Research Projects\Test_crop_app\crop-monitoring-app')
df1 = xr.open_dataset(r'MODIS_netcdf.nc')
df1.load()
df = df1['CMG 0.05 Deg Monthly EVI'].isel(time =0)
cs = df1['CMG 0.05 Deg Monthly EVI'].isel(time =0).plot()
import numpy as np

vals = df.values
lats = df.latitude.values
lons = df.longitude.values
import pylab as py
lats, lons = np.meshgrid(lats, lons)
lats = lats.T
lons = lons.T
# py.figure()
# cs = py.contourf(lons, lats, vals, levels = np.arange(-0.1,1, 0.1))
# py.show()

idx = vals > 0.0
lats, lons = np.meshgrid(lats, lons)
lats = lats.T
lons = lons.T
vals = vals[idx]
lats = lats[idx]
lons = lons[idx]
import pandas as pd
import numpy as np
df = pd.DataFrame({'data':vals,'lat':lats,'lon':lons})
import json
import pandas as pd
from geojson import Feature, FeatureCollection, Point, Polygon

# columns used for constructing geojson object
features = df.apply(
    lambda row: Feature(geometry=Point((float(row['lon']), float(row['lat'])))),
    axis=1).tolist()

# all the other columns used as properties
properties = df.drop(['lat', 'lon'], axis=1)
properties['data'] = properties['data'].apply(lambda a: str(a))
properties = properties.to_dict('records')

# whole geojson object
feature_collection = FeatureCollection(features=features, properties=properties)
with open('test.geojson', 'w', encoding='utf-8') as f:
    json.dump(feature_collection, f, ensure_ascii=False)

#observations = df['CMG 0.05 Deg Monthly NDVI']
import geojsoncontour

#Converting matplotplib contour plot to geojson
geojson = geojsoncontour.contourf_to_geojson(
    contourf=cs,
    ndigits=4,
   )

#reading geojson as dict
price_geojson=eval(geojson)
# !/usr/bin/env python
# coding: utf-8

# Creating empty array to fill with prices
arr_temp = np.ones([len(price_geojson["features"]), 2])

for i in range(0, len(price_geojson["features"])):
    price_geojson["features"][i]["id"] = i

    # Filling array with price and Id for each geojson spatial object. Z value from contour plot will be stored as title
    arr_temp[i, 0] = i
    arr_temp[i, 1] = float(price_geojson["features"][i]["properties"]["title"].split('-')[-1])

# Transforming array to df
df_contour = pd.DataFrame(arr_temp, columns=["Id", "Price"])

import plotly.graph_objects as go


import plotly.express as px
import geopandas as gpd

gdf = gpd.GeoDataFrame(price_geojson['features'])
fig = px.choropleth_mapbox(geojson=price_geojson['features'])#, locations=df_contour['Price'].values, color=df_contour['Price'].values,
                           #color_continuous_scale="Viridis",
                           #mapbox_style="carto-positron",
                           #zoom=3, center = {"lat": -37.0902, "lon": 175.7129},
                           #labels={'Price':'unemployment rate'}
                          #)
#f#ig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
plot(fig, filename='name.html')



# Selecting a central city point to center all graphs around - Swietokrzyska Subway
center_coors = 52.235176, 21.008393

trace = go.Choroplethmapbox(
    geojson=price_geojson['features'],
    z=df_contour.Price,
    colorscale="jet",
    marker_line_width=10,

    marker=dict(opacity=0.5)
)

layout = go.Layout(
    title="Warsaw Real Estate prices heatmap [PLN/m2]",
    title_x=0.4,
    height=800,
    margin=dict(t=80, b=0, l=0, r=0),
    font=dict(color='dark grey', size=18),

    mapbox=dict(
        center=dict(
            lat=-39,
            lon=174.5
        ),
        zoom=7,
        style="carto-positron"
    )

)

figure = dict(
    data=[trace],
    layout=layout,

)

from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot

plot(figure, filename='name.html')



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
                                 html.P('Refresh the App on Loading (In browser)',style={'color': 'k'})
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
                              marker=dict(size=7, showscale=True, color=vals2, colorscale ='rdylgn',cmin=0.01, cmax=0.8),
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
        'data': [trace1],
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


