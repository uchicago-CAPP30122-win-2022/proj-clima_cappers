import sqlite3
from turtle import title
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from linearmodels import PanelOLS
from sklearn.impute import KNNImputer
import sys

from dash_app.helpers.dynamic_dropdown_list import indicators_lst, country_lst, regions_lst
from dash_app.helpers.layer_1 import extract_map_data, extract_bar_data, trend_df
from dash_app.helpers.layer_2 import *
from dash_app.helpers.layer_3 import *
from dash_app.helpers.regression import *


connection = sqlite3.connect("clima_cappers/data/indicators.sqlite3", check_same_thread=False)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

econ_indicators_lst = [("GDP constant (change)", "gdp_constant_change"),
("GDP per capita", "gdp_capita"), ("Volume of imports (change)", "vol_imports_change"),
("Volume of exports (change)", "vol_exports_change"), ("Population", "population"),
("GDP (current)", "gdp_current"), ("Energy usage", "energy_usage"), ("Imports", "imports_gns"),
("Expprts", "exports_gns"),]

climate_indicators_lst = [("C02 emissions per capita", "co2_emissions_capita"),
("C02 emissions(kt)", "co2_emissions_kt"), ("Forest area", "forest_area"),
("Electricity production (hydro)", "electricity_pro_hydro"), 
("Electricity production (Natural gas)", "electricity_pro_natural_gas"),
("Electricity production (Nuclear)", "electricity_pro_nuclear"),
("Electricity production (Oil)", "electricity_pro_oil"),
("Electricity production (Coal)", "electricity_pro_coal"),
("Electricity production (Fossil fuels)", "electricity_pro_fossils"),
("Electricity production (Renewables)", "electricity_pro_renewable"),
("PM 2.5", "pm_25"),
("SF6 emissions", "sf6_emissions"),
("Greenhouse gases(total)", "ghg_total"),
("Greenhouse gases(growth)", "ghg_growth"),
("Greenhouse gases(capita)", "ghg_capita"),
("Mean surface temperature", "mean_surface_temp")]

# creating date_dict for year slider
date_dict = {}
for date in range(1995, 2021):
    date_dict[date] = str(date)


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Climate vs Economy'
app.layout = html.Div([html.Div([html.H1("Climate Change and the Economy")],
                                style={'textAlign': "center", "padding-bottom": "120"}
                               ),
                        html.Hr(className='gap'),
                        html.Div([html.Span('''Through the following analysis, we seek to
                        gauge the correlations between climate and economic indicators for
                        195 countries across 26 years.''')],
                                style={"padding-bottom": "120"}
                               ),
                        html.Hr(className='gap'),
                        html.Div([html.H3("Comparing indicators - Single year")],
                                style={'textAlign': "center", "padding-bottom": "50"}
                               ),
                        html.Div([html.Span('''The maps below juxtapose countries' performance
                            on climate vs economic indicators for a particular year chosen on
                            the slider.''')],
                                style={"text-align": "center", "padding-top": 10}
                               ),
                        html.Hr(className='gap'),
                        html.Div([dcc.Slider(1995, 2021,
                                    step=None,
                                    marks=date_dict,
                                    value=2002,
                                    id='year-slider')], className="row"),
                        html.Hr(className='gap'),
                        html.Div(className="row",
                        children = [
                            html.Div(className="six columns", 
                            children = [
                            dcc.Dropdown(id="econ-param", value='gdp_constant_change',
                                            options=indicators_lst(econ_indicators_lst)
                                            # style={"display": "block", "margin-left": "auto", "margin-right": "auto",
                                            #         "width": "70%"}
                                            ),
                            dcc.Graph(id="econ-map", style={'width': '80vh', 'height': '80vh'})
                            ]),
                            html.Div(className="six columns", 
                            children = [
                            dcc.Dropdown(id="climate-param", value='co2_emissions_kt',
                                            options=indicators_lst(climate_indicators_lst)),
                            dcc.Graph(id="climate-map", style={'width': '60vh', 'height': '60vh',
                                    "margin-left": "auto", "margin-right": "auto"})
                            ])
                        ]),
                        html.Div(className="row",
                        children = [
                            html.Div(className="six columns", 
                            children = [
                            dcc.Graph(id="econ-bar", style={'max-height': '100%', 'max-width': '100%',
                                                 'width': 'auto', 'height': 'auto'}),
                            ]),
                            html.Div(className="six columns", 
                            children = [
                            dcc.Graph(id="climate-bar", style={'max-height': '100%', 'max-width': '100%',
                                                 'width': 'auto', 'height': 'auto'})
                            ])
                        ]),
                        html.Hr(className='gap'),
                        html.Div([html.H3("Comparing indicators - Aggregated by years")],
                                style={'textAlign': "center", "padding-bottom": "50"}
                               ),
                        html.Div([html.Span('''The maps below juxtapose countries' performance
                            on climate vs economic indicators for a range of years chosen on
                            the slider.''')],
                                style={"text-align": "center", "padding-top": 10}
                               ),
                        html.Hr(className='gap'),
                        html.Div([dcc.RangeSlider(1995, 2020,
                                    step=None,
                                    marks=date_dict,
                                    value=[2002, 2007],
                                    id='agg-slider')], className="row"),
                        html.Hr(className='gap'),
                        html.Div(className="row",
                        children = [
                            html.Div(className="six columns", 
                            children = [
                            dcc.Dropdown(id="econ-param-agg", value='gdp_current',
                                            options=[{'label': "GDP, current price, PPP (in billions)", 'value': 'gdp_current'},
                                                    {'label': "GDP per capita", 'value': 'gdp_capita'},
                                                    {'label': "Volume of Exports", 'value': 'exports_gns'},
                                                    {'label': "Volume of Imports", 'value': 'imports_gns'}]),
                            dcc.Graph(id="econ-map-agg", style={'width': '80vh', 'height': '80vh'})
                            ]),
                            html.Div(className="six columns", 
                            children = [
                            dcc.Dropdown(id="climate-param-agg", value='co2_emissions_kt',
                                            options=[{'label': "C02 emissions(kt)", 'value': 'co2_emissions_kt'},
                                                    {'label': "C02 emissions per capita", 'value': 'co2_emissions_capita'},
                                                    {'label': "PM 2.5", 'value': 'pm_25'},
                                                    {'label': "Greenhouse emission per capita", 'value': 'ghg_capita'},
                                                    {'label': "Mean Surface Temperature", 'value': 'mean_surface_temp'}]),
                            dcc.Graph(id="climate-map-agg", style={'width': '80vh', 'height': '80vh',
                                    "margin-left": "auto", "margin-right": "auto"})
                            ])
                        ]),
                        html.Hr(className='gap'),
                        html.Div([html.H3("Trend Chart")],
                                style={'textAlign': "center", "padding-bottom": "50"}
                               ),
                        html.Div([html.Span('''The chart below compares the trend of multiple
                            indicators for a particular country over a period of 26 years.''')],
                                style={"text-align": "center", "padding-top": 10}
                               ),
                        html.Hr(className='gap'),
                        html.Div(className="row",
                        children = [
                            html.Div(className='row', children=[
                                html.Div(children=[
                                    html.Div(className='four columns', children=[
                                         dcc.Dropdown(id="country", value='IND',
                                            options=country_lst(),
                                            style={"width": "100%"})
                                    ]),
                                    html.Div(className='eight columns', children=[
                                         dcc.Dropdown(id="multi-params", value=['gdp_constant_change',
                                                                         'vol_imports_change'],
                                            options=indicators_lst(econ_indicators_lst + climate_indicators_lst),
                                            multi=True,
                                            style={"width": "100%"})
                                    ])
                                ])
                            ]),
                            html.Hr(className='gap'),
                            dcc.Graph(id="trend-chart", style={'width': '140vh', 'height': '70vh'})
                        ]),
                        html.Hr(className='gap'),
                        html.Div([html.H3("Bubble chart")],
                                style={'textAlign': "center", "padding-bottom": "50"}
                               ),
                        html.Div([html.Span('''The map below estimates the consolidated performance of
                            a country on both climate and economic indicators.''')],
                                style={"text-align": "center", "padding-top": 10}
                               ),
                        html.Hr(className='gap'),
                        html.Div([dcc.RangeSlider(1995, 2020,
                                    step=None,
                                    marks=date_dict,
                                    value=[2002, 2007],
                                    id='bubble-slider')], className="row"),
                        html.Hr(className='gap'),
                        dcc.Graph(id="bubble-chart"),
                        html.Hr(className='gap'),
                        html.Div([html.H3("Regressions")],
                                style={'textAlign': "center", "padding-bottom": "50"}
                               ),
                        html.Div([html.Span('''<Fill in summary>''')],
                                style={"text-align": "center", "padding-top": 10}
                               ),
                        html.Hr(className='gap'),
                        html.Div(className="row",
                        children = [
                            html.Div(className='row', children=[
                                html.Div(children=[
                                    html.Div(className='four columns', children=[
                                         dcc.Dropdown(id="regions-list", value='Western Asia',
                                            options=regions_lst(),
                                            style={"width": "100%"})
                                    ]),
                                    html.Div(className='eight columns', children=[
                                         dcc.Dropdown(id="control-vars-list", value='',
                                            options=[{'label': "Imports", 'value': 'imports_gns'},
                                                    {'label': "Exports", 'value': 'exports_gns'},
                                                    {'label': "Population", 'value': 'e.population'}],
                                            multi=True,
                                            style={"width": "100%"})
                                    ])
                                ])
                            ]),
                            html.Hr(className='gap'),
                            dcc.Graph(id="scatter-bubble", style={'width': '120vh', 'height': '70vh'}),
                            dash_table.DataTable(id='reg-table',
                                    columns=[
                                            {'name': 'parameter', 'id': 'parameter'},
                                            {'name': 'std_error', 'id': 'std_error'},
                                            {'name': 'p-value', 'id': 'pvalue'}]
                                )
                        ]),
                        html.Hr(className='gap')
                       ], className="container")

@app.callback(
    dash.dependencies.Output("econ-map", "figure"),
    [dash.dependencies.Input("econ-param", "value"),
     dash.dependencies.Input("year-slider", "value")]
)
def update_econ_map(indicator, year):
    df = extract_map_data(indicator, "econ_indicators", str(year))
    df["hover_text"] = df["country"] + ": " + df[indicator].apply(str)
 
    trace = go.Choropleth(locations=df['iso_code'],z=df[indicator],
                          text=df['hover_text'],
                          hoverinfo="text",
                          marker_line_color='white',
                          autocolorscale=False,
                          reversescale=True,
                          colorscale="RdBu",marker={'line': {'color': 'rgb(180,180,180)','width': 0.5}},
                          colorbar={"thickness": 10,"len": 0.68,"x": 0.98,"y": 0.50})   
    return {"data": [trace],
            "layout": go.Layout(height=700, geo={'showframe': True,'showcoastlines': False,
                                                                      'projection': {'type': "mercator"}},
                                                                      margin=dict(l=00, r=200, b=0, t=0))}

@app.callback(
    dash.dependencies.Output("climate-map", "figure"),
    [dash.dependencies.Input("climate-param", "value"),
     dash.dependencies.Input("year-slider", "value")]
)
def update_climate_map(indicator, year):
    df = extract_map_data(indicator, "climate_indicators", str(year))
    df["hover_text"] = df["country"] + ": " + df[indicator].apply(str)

    trace = go.Choropleth(locations=df['iso_code'],z=df[indicator],
                          text=df['hover_text'],
                          hoverinfo="text",
                          marker_line_color='white',
                          autocolorscale=False,
                          reversescale=True,
                          colorscale="RdBu",marker={'line': {'color': 'rgb(180,180,180)','width': 0.5}},
                          colorbar={"thickness": 10,"len": 0.80,"x": 0.98,"y": 0.50})   
    return {"data": [trace],
            "layout": go.Layout(height=700,geo={'showframe': True,'showcoastlines': False,
                                                                      'projection': {'type': "mercator"}},
                                                                      margin=dict(l=0, r=0, b=60, t=60))}


@app.callback(
    dash.dependencies.Output("econ-map-agg", "figure"),
    [dash.dependencies.Input("econ-param-agg", "value"),
     dash.dependencies.Input("agg-slider", "value")]
)
def update_econ_agg_map(indicator, year):
    df = extract_agg_data(indicator, "econ_indicators", year)
    df["hover_text"] = df["country"] + ": " + df[indicator].apply(str)
 
    trace = go.Choropleth(locations=df['iso_code'],z=df[indicator],
                          text=df['hover_text'],
                          hoverinfo="text",
                          marker_line_color='white',
                          autocolorscale=False,
                          reversescale=True,
                          colorscale="RdBu",marker={'line': {'color': 'rgb(180,180,180)','width': 0.5}},
                          colorbar={"thickness": 10,"len": 0.68,"x": 0.98,"y": 0.50})   
    return {"data": [trace],
            "layout": go.Layout(height=700, geo={'showframe': True,'showcoastlines': False,
                                                                      'projection': {'type': "mercator"}},
                                                                      margin=dict(l=00, r=200, b=0, t=0))}


@app.callback(
    dash.dependencies.Output("climate-map-agg", "figure"),
    [dash.dependencies.Input("climate-param-agg", "value"),
     dash.dependencies.Input("agg-slider", "value")]
)
def update_climate_agg_map(indicator, year):
    df = extract_agg_data(indicator, "climate_indicators", year)
    df["hover_text"] = df["country"] + ": " + df[indicator].apply(str)
 
    trace = go.Choropleth(locations=df['iso_code'],z=df[indicator],
                          text=df['hover_text'],
                          hoverinfo="text",
                          marker_line_color='white',
                          autocolorscale=False,
                          reversescale=True,
                          colorscale="RdBu",marker={'line': {'color': 'rgb(180,180,180)','width': 0.5}},
                          colorbar={"thickness": 10,"len": 0.68,"x": 0.98,"y": 0.50})   
    return {"data": [trace],
            "layout": go.Layout(height=700, geo={'showframe': True,'showcoastlines': False,
                                                                      'projection': {'type': "mercator"}},
                                                                      margin=dict(l=00, r=200, b=0, t=0))}


@app.callback(
    dash.dependencies.Output("econ-bar", "figure"),
    [dash.dependencies.Input("econ-param", "value"),
     dash.dependencies.Input("year-slider", "value")]
)
def econ_bar_chart(indicator, year):
    df = extract_bar_data(indicator, "econ_indicators", str(year))

    barchart = px.bar(
        data_frame=df,
        x='country',
        y=indicator,
        title= "Top 5 countries ({})".format(indicator),
        #color="INDEX_NAME",
        opacity=0.9,
        barmode='group')

    return barchart


@app.callback(
    dash.dependencies.Output("climate-bar", "figure"),
    [dash.dependencies.Input("climate-param", "value"),
     dash.dependencies.Input("year-slider", "value")]
)
def climate_bar_chart(indicator, year):
    df = extract_bar_data(indicator, "climate_indicators", str(year))

    barchart = px.bar(
        data_frame=df,
        x='country',
        y=indicator,
        title= "Top 5 countries ({})".format(indicator),
        #color="INDEX_NAME",
        opacity=0.9,
        barmode='group')

    return barchart


@app.callback(
    dash.dependencies.Output("trend-chart", "figure"),
    [dash.dependencies.Input("multi-params", "value"),
     dash.dependencies.Input("country", "value")]
)
def plot_trend_chart(indicator_lst, country):
    df = trend_df(indicator_lst, country)

    fig = px.line(df,
        x="year", y="value", color='indicators')
    
    return fig


@app.callback(
    dash.dependencies.Output("bubble-chart", "figure"),
    [dash.dependencies.Input("bubble-slider", "value")]
)
def plot_bubble_chart(year):
    df = extract_bubble_data(year)

    fig = px.scatter_geo(df, locations="iso_code", color="net_growth_rate",
                    color_discrete_map = {'Positive Growth-Emission Difference': 'rgb(0,0,255)',
                                        'Negative Growth-Emission Difference': 'rgb(255,0,0)'},
                     hover_name="country", size="difference",
                     projection="natural earth")
    
    return fig


@app.callback(
    dash.dependencies.Output("scatter-bubble", "figure"),
    [dash.dependencies.Input("regions-list", "value")]
)
def plot_scatter_bubble_chart(region):
    df = extract_countries(region)

    fig = px.scatter(df, x="log_ghg_total", y="log_gdp_current",
            animation_frame="year", animation_group="country",
	         size="population", hover_name="country", size_max=60,
            range_y=[1,13])
    
    return fig


@app.callback(
    dash.dependencies.Output("reg-table", "data"),
    [dash.dependencies.Input("control-vars-list", "value"),
    dash.dependencies.Input("regions-list", "value")]
)
def display_reg_table(controls, region):
    reg_results = regression_df(controls, region)
    params = pd.DataFrame(reg_results.params)
    std_errors = pd.DataFrame(reg_results.std_errors)
    pvalues = pd.DataFrame(reg_results.pvalues)
    reg_df = pd.concat([params, std_errors, pvalues], axis=1, join="inner")
    
    return reg_df.to_dict('records')


def run():
    app.run_server(debug=True, port=8051)


