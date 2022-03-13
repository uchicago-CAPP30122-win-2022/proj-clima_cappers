import sqlite3
import dash
from dash import dcc
from dash import html
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


connection = sqlite3.connect("indicators.sqlite3", check_same_thread=False)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# creating date_dict for year slider
date_dict = {}
for date in range(1995, 2021):
    date_dict[date] = str(date)

def extract_map_data(year_input):
    
    query1 = ''' SELECT country, iso_code, gdp_current FROM econ_indicators WHERE year BETWEEN {} AND {}'''. \
                format(year_input[0], year_input[1])
    
    query2 = ''' SELECT country, iso_code, co2_emissions_kt FROM climate_indicators WHERE year BETWEEN {} AND {}'''. \
                format(year_input[0], year_input[1])
    
    df_econ = pd.read_sql_query(query1, connection)
    df_climate = pd.read_sql_query(query2, connection)
    df_econ['gdp_current'] = pd.to_numeric(df_econ['gdp_current'], downcast="float")
    df_climate['co2_emissions_kt'] = pd.to_numeric(df_econ['co2_emissions_kt'], downcast="float")

    df_econ_agg= aggregate_weight(df_econ, 'gdp_current')
    df_climate_agg= aggregate_weight(df_climate, 'co2_emissions_kt')
    df_climate_agg= df_climate_agg.drop('country', axis=1)
    merge_econ_climate = pd.merge(df_econ_agg, df_climate_agg, how= "left", on=["iso_code"])
    nan_values = merge_econ_climate[merge_econ_climate.isna().any(axis=1)]
    merge_econ_climate.dropna(axis=0, how='any', thresh=None, subset=None, inplace=True)
    merge_econ_climate['difference'] = merge_econ_climate['gdp_current'] - merge_econ_climate['co2_emissions_kt']
    merge_econ_climate= merge_econ_climate.append(nan_values)
    merge_econ_climate= merge_econ_climate.drop(['gdp_current', 'co2_emissions_kt'], axis=1)

    return merge_econ_climate


def w_avg(df_weigh, values):
    d = df_weigh[values]
    last= d.iloc[-1]
    first= d.iloc[0]
    
    if pd.isna(first) or pd.isna(last):
        return np.NaN
    else:
        ratio= (last/first)**(1/len(d))-1
        return ratio

def aggregate_weight(df_get, indicator):
    df_new= df_get.groupby(['iso_code', 'country'], as_index=False).apply(w_avg, indicator)
    df_new.rename(columns = {None: indicator}, inplace = True)
    return df_new

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Climate vs Economy'
app.layout = html.Div([html.Div([html.H1("Climate Change and the Economy")],
                                style={'textAlign': "center", "padding-bottom": "30"}
                               ),
                        html.Div(className="row",
                        children = [
                            html.Div(className="six columns", 
                            children = [
                            html.Div([html.Span("Metric to display : ", className="six columns",
                                        style={"text-align": "right", "width": "40%", "padding-top": 10}),
                                dcc.Dropdown(id="econ-param", value='gdp_current',
                                            options=[{'label': "GDP, current price, PPP (in billions)", 'value': 'gdp_current'},
                                                    {'label': "GDP per capita", 'value': 'gdp_capita'}],
                                            style={"display": "block", "margin-left": "auto", "margin-right": "auto",
                                                    "width": "70%"},
                                            className="six columns")], className="row"),
                            dcc.Graph(id="econ-map", style={'width': '90vh', 'height': '90vh'})
                            ]),
                            html.Div(className="six columns", 
                            children = [
                            html.Div([html.Span("Metric to display : ", className="six columns",
                                        style={"text-align": "right", "width": "40%", "padding-top": 10}),
                                dcc.Dropdown(id="climate-param", value='co2_emissions_kt',
                                            options=[{'label': "C02 emissions(kt)", 'value': 'co2_emissions_kt'},
                                                    {'label': "C02 emissions per capita", 'value': 'co2_emissions_capita'},
                                                    {'label': "PM 2.5", 'value': 'pm_25'},
                                                    {'label': "Volume of Exports", 'value': 'exports_gns'},
                                                    {'label': "Volume of Imports", 'value': 'imports_gns'},
                                                    {'label': "Greenhouse emission per capita", 'value': 'ghg_capita'},
                                                    {'label': "Mean Surface Temperature", 'value': 'mean_surface_temp'},],
                                            style={"display": "block", "margin-left": "auto", "margin-right": "auto",
                                                    "width": "70%"},
                                            className="six columns")], className="row"),
                            dcc.Graph(id="climate-map", style={'width': '90vh', 'height': '90vh'})
                            ])
                        ]),
                        html.Div([dcc.RangeSlider(1995, 2020, 1,
                                    value=[2002, 2007],
                                    id='my-range-slider')], className="row"),
                        html.Div([
                            # Dhruv's container
                        ], className="container"),
                        html.Div([
                            # Kaveri's container
                        ], className="container")
                       ], className="container")

@app.callback(
    dash.dependencies.Output("econ-map", "figure"),
    [dash.dependencies.Input("econ-param", "value"),
     dash.dependencies.Input("my-range-slider", "value")]
)
def update_figure(indicator, year):
    print("hello econ")
    df = extract_map_data(indicator, "econ_indicators", year)

    trace = go.Choropleth(locations=df['iso_code'],z=df[indicator],
                          text=df['country'],
                          hoverinfo="text",
                          marker_line_color='white',
                          autocolorscale=False,
                          reversescale=True,
                          colorscale="RdBu",marker={'line': {'color': 'rgb(180,180,180)','width': 0.5}},
                          colorbar={"thickness": 10,"len": 0.3,"x": 0.9,"y": 0.7,
                                    'title': {"text": 'persons', "side": "bottom"},
                                    'tickvals': [ 2, 10],
                                    'ticktext': ['100', '100,000']})   
    return {"data": [trace],
            "layout": go.Layout(height=800,geo={'showframe': False,'showcoastlines': False,
                                                                      'projection': {'type': "miller"}})}


@app.callback(
    dash.dependencies.Output("climate-map", "figure"),
    [dash.dependencies.Input("climate-param", "value"),
     dash.dependencies.Input("my-range-slider", "value")]
)
def update_figure(indicator, year):
    print("Hello climate")
    df = extract_map_data(indicator, "climate_indicators", year)
    trace = go.Choropleth(locations=df['iso_code'],z=df[indicator],
                          text=df['country'],
                          hoverinfo="text",
                          marker_line_color='white',
                          autocolorscale=False,
                          reversescale=True,
                          colorscale="RdBu",marker={'line': {'color': 'rgb(180,180,180)','width': 0.5}},
                          colorbar={"thickness": 10,"len": 0.3,"x": 0.9,"y": 0.7,
                                    'title': {"text": 'persons', "side": "bottom"},
                                    'tickvals': [ 2, 10],
                                    'ticktext': ['100', '100,000']})   
    return {"data": [trace],
            "layout": go.Layout(height=800,geo={'showframe': False,'showcoastlines': False,
                                                                      'projection': {'type': "miller"}})}

if __name__ == '__main__':
    app.run_server(debug=True, port=8052)