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
import json
from dask import delayed, compute
import numpy as np
import geojsoncontour

def contour_to_geojson(lats_grid, lons_grid, values, n_levels = np.arange(14, 25, 0.2)):
    """

    :param lats_grid: Must be in the shape of (n by m)
    :param lons_grid: Must be in the shape of (n by m)
    :param values: must be in the shape of (n by m)
    :return: Returns a geojson for cloropleth plotting
    """
    cs = py.contourf(lons_grid, lats_grid, values, levels = n_levels)
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

n_previous =50
filename = 'CRW_SST'
key_name =filename
#os.chdir(r'C:\Users\rampaln\OneDrive - NIWA\Repositories\crop-monitoring-app')
preprocess = True
df1 = xr.open_dataset(r'high_res_sst.nc')
clim = df1.groupby(df1.time.dt.month).mean()
df1 = df1.groupby(df1.time.dt.month) - clim
df1 = df1.load().isel(time  = slice(-1 * n_previous, None))



def save_json(output_dir =r'.\assets',
              file_dir = r'high_res_sst.nc',
              filename = 'CRW_SST', n_previous =n_previous, preprocess = True):
    df1 = xr.open_dataset(file_dir)
    clim = df1.groupby(df1.time.dt.month).mean()
    df1 = df1.groupby(df1.time.dt.month) - clim
    df1 = df1.load().isel(time  = slice(-1 * n_previous, None))
    lats = df1.latitude.values
    lons = df1.longitude.values
    # Load the data
    if preprocess:
        for slider_time in df1.time.to_index():
            df = df1[filename].sel(time=slider_time)
            time_str = str(slider_time.strftime("%Y-%m-%d"))

            vals = df.values

            Ids, geojson = contour_to_geojson(lats, lons, vals, 25)
            Ids.to_csv(f'{output_dir}/Ids_{time_str}.csv')

            with open(f'{output_dir}/geojson_{time_str}.json', 'w') as f:
                json.dump(geojson, f)
    return df1.time.to_index(), lats, lons

print("Computing jsons")
times, lats, lons = save_json(preprocess=False)



server = flask.Flask(__name__)
colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}
server = flask.Flask(__name__)
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, server = server)
#app.config.suppress_callback_exceptions = True
dict1 = {}
for i in range(0, len(times), 6):
    dict1[i] = times[i].strftime("%Y %b")
app.layout = html.Div(style={'backgroundColor': colors['background'],'body':0},
    children=[
       html.Div(
                 children=[
                    html.Div(className='six columns',
                             children=[
                                 html.H2('NOAA Coral Reef SST',style={'color': 'k'}),
                                 html.H4('Click on the Map to Plot the Time Series',style={'color': 'k'}),
                                 dcc.Interval(interval=500),
                                 html.Div(
                                     className='div-for-dropdown',
                                     children=[
                                         dcc.Dropdown(
                                             id='datetimemonth-dropdown',
                                             options=[{'label': k, 'value': k} for k in [key_name]],
                                             value=key_name,
                                             placeholder="Select Variable",
                                             style=dict(width='40%',
                                                 display='inline-block',
                                                 verticalAlign="middle")),
                                        dcc.Interval(interval=500),
                                        dcc.Slider(id ="time-slider",min=0, #the first date
                                                       max=len(times)-1, #the last date
                                                       value=len(times)-3,step =1,
                                                   tooltip={'always_visible': True}, marks=dict1),
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
Ids_ = []
geojsons = []
for slider_time in range(len(times)):
    time = times[slider_time]
    time_str = time.strftime("%Y-%m-%d")
    Ids_.append(pd.read_csv(f'./assets/Ids_{time_str}.csv', index_col=0))
    with open(f'./assets/geojson_{time_str}.json', 'r') as f:
        geojson = json.load(f)
    geojsons.append(geojson)

@app.callback(dash.dependencies.Output('funnel-graph', 'figure'),
              [dash.dependencies.Input('datetimemonth-dropdown', 'value'),
               dash.dependencies.Input("time-slider", "value"),
               dash.dependencies.Input("zoom-slider", "value")])
def update_graph(filename, slider_time, zoom_slider):
    time = times[slider_time]
    time_str  = time.strftime("%Y-%m-%d")
    Ids = Ids_[slider_time]#
    geojson = geojsons[slider_time]
    #pd.read_csv(f'./assets/Ids_{time_str}.csv', index_col=0)
    # with open(f'./assets/geojson_{time_str}.json', 'r') as f:
    #     geojson = json.load(f)

    trace2 = go.Choroplethmapbox(
    geojson=geojson,
    locations=Ids.Id,
    z=Ids.AirTemperature,
    colorscale="RdBu_r",
    marker_line_width=0,

    marker=dict(opacity=0.9))

    vals = df1['CRW_SST'].sel(time = time).values
    lats, lons = df1.latitude.values, df1.longitude.values

    
    lats, lons = np.meshgrid(lats, lons)
    lats = lats.T[::3,::3]
    lons = lons.T[::3,::3]
    idx = vals[::3,::3] > -8.0
    lats2 = lats[idx].ravel()
    lons2 = lons[idx].ravel()
    vals2 = vals[::3,::3][idx].ravel()
    # Note you should only plot these scatter points on the first iteration and then just use them for clicking on the points
    trace1 = go.Scattermapbox(lat=lats2,
                              lon=lons2,
                              mode='markers+text',
                              marker=dict(size=7, showscale=False, color=vals2, colorscale ='RdBu_r',cmin=0.01, cmax=0.8, opacity =0.01),
                              textposition='top right',
                              hovertext=[f"SST Anomaly %.2f" % i for i in vals2])
    mapbox = dict(
        center=dict(
            lat=-41,
            lon=170
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
                      barmode='stack', mapbox=mapbox, height=550, width=550,template= 'seaborn', font=dict(
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
def update_pre_callback(filename, foo_click_data,time_slider, key_name = key_name):
    delta = 0.05
    try:
        lats, lons = foo_click_data#pprint.pformat(foo_click_data)['points']['lat'],\

                # pprint.pformat(foo_click_data)['points']['lon']
    except TypeError:
        lats = -41.5
        lons = 167.5 # Choosing a random location
    # value_data = df1[key_name].isel(time=time_slider).sel(latitude = slice(lats +delta, lats -delta),
    #                        longitude = slice(lons-delta, lons+delta)).mean(["latitude","longitude"])
    # time_value = pd.to_datetime(value_data.time.values)


    df = df1[filename].sel(latitude = slice(lats +delta, lats -delta),
                           longitude = slice(lons-delta, lons+delta)).mean(["latitude","longitude"])
    df2 = df.groupby(df.time.dt.month).apply(demean)
    df2 = df2.to_dataframe()
    #print(df2)

    # df = value_data.to_dataframe()
    # xdata = df.loc[time_value]
    # index = df.index.intersection([time_value])
    # xdata2 = df2.loc[time_value]
    # df2 = df.groupby(df.time.dt.month).apply(demean)
    # df2 = df2.to_dataframe()
    #trace3 = go.Scatter(x = index, y = [xdata[filename]], mode ='markers+text',name = key_name,marker=dict(size=14, color='blue'))
    # trace1 = go.Scatter(x=df.index, y=df[filename], name =f'EVI', mode ='lines', textposition = 'bottom center')
    trace2 = go.Scatter(x=df2.index, y=df2[filename], name =f'SST Anomally', mode='lines', textposition = 'bottom center')
    # trace4 = go.Scatter(x=index, y=[xdata2[filename]], mode='markers+text',
    #                     marker=dict(size=14, color='red'),name = 'EVI Anomally')

    return {
        'data': [trace2],
        'layout':
        go.Layout(
            title='{} Time-Series'.format(filename),#,"%.2f" % lats,"%.2f" % lons),
            barmode='stack', width = 650, height =550,# colorway=["#5E0DAC", '#FF4F00', '#375CB1', '#FF7400', '#FFF400', '#FF0056'],
            template='seaborn',
            hovermode='x',
            autosize=True,
            font=dict(
                family="Courier New, monospace",
                size=10,
            ),
            plot_bgcolor = 'rgba(0, 0, 0, 0)',
            margin={'t': 100},yaxis=dict(range=[-3,3]),
        )
    }



if __name__ == '__main__':
    app.run_server(debug=True)


