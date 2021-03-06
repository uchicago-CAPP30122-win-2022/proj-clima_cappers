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

from helpers.dynamic_dropdown_list import indicators_lst, country_lst, regions_lst
from helpers.layer_1 import extract_map_data, extract_bar_data, trend_df
from helpers.layer_2 import *
from helpers.layer_3 import *
from helpers.regression import *


connection = sqlite3.connect("data/indicators.sqlite3", check_same_thread=False)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

econ_indicators_lst = [("GDP constant (change)", "gdp_constant_change"),
("GDP per capita (PPP 2017 Intl $)", "gdp_capita"), ("Volume of imports (change)", 
"vol_imports_change"), ("Volume of exports (change)", "vol_exports_change"), 
("Population", "population"), ("GDP current PPP intl $", "gdp_current"), 
("Energy usage (kg of oil equivalent per capita)", 
"energy_usage"), ("Imports (constant 2015 US$)", "imports_gns"),
("Expprts(constant 2015 US$)", "exports_gns"),]

climate_indicators_lst = [("C02 emissions per capita (metric tons)", "co2_emissions_capita"),
("C02 emissions(kt)", "co2_emissions_kt"), ("Forest area (% of land area)", "forest_area"),
("Electricity production-hydro (% of total)", "electricity_pro_hydro"), 
("Electricity production-Natural gas (% of total)", "electricity_pro_natural_gas"),
("Electricity production-Nuclear (% of total)", "electricity_pro_nuclear"),
("Electricity production- Oil (% of total)", "electricity_pro_oil"),
("Electricity production- Coal (% of total)", "electricity_pro_coal"),
("Electricity production- Fossil fuels (% of total)", "electricity_pro_fossils"),
("Electricity production- Renewables (% of total)", "electricity_pro_renewable"),
("PM 2.5(mg per cubic meter)", "pm_25"),
("SF6 emissions (thousand metric tons of CO2 equivalent)", "sf6_emissions"),
("Greenhouse gases-total (kt of CO2 equivalent)", "ghg_total"),
("Greenhouse gases(growth)", "ghg_growth"),
("Greenhouse gases(tons/capita)", "ghg_capita"),
("Mean surface temperature (change)", "mean_surface_temp")]

# creating date_dict for year slider
date_dict = {}
for date in range(1995, 2021):
    date_dict[date] = str(date)


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Climate vs Economy'
app.layout = html.Div([html.Div([html.H1("Analysing Climate Change and Economic Growth"
                                            " indicators over time")],
                                style={'textAlign': "center", "padding-bottom": "120"}
                               ),
                        html.Hr(className='gap'),
                        html.Div([html.Span('''In this project, we are mapping trends in economic
                        and climate change indicators over the years for every country. Change in 
                        economic parameters and climate change indicators are very closely 
                        related. The aim of this project is to allow users to use our application 
                        as a tool to probe into any climate or economic related research questions
                        that they might have.''')],
                                style={"padding-bottom": "120"}
                               ),
                        html.Hr(className='gap'),
                        html.Div([html.H3("Comparing indicators - Single year")],
                                style={'textAlign': "center", "padding-bottom": "50"}
                               ),
                        html.Div([html.Span('''The maps below juxtapose countries' performance
                            on climate vs economic indicators for a particular year chosen on
                            the slider.''')],
                                style={"text-align": "left", "padding-top": 10}
                               ),
                        html.Div([html.Span('''How to use-''')],
                                style={"text-align": "left", "padding-top": 10}
                               ),
                        html.Div([html.Span('''(a) select an indicator from climate parameters''')],
                                style={"text-align": "left", "padding-top": 10}
                               ),
                        html.Div([html.Span('''(b) select an indicator from economic parameters''')],
                                style={"text-align": "left", "padding-top": 10}
                               ),
                        html.Div([html.Span('''(c) select year from the year slider''')],
                                style={"text-align": "left", "padding-top": 10}
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
                        html.Div([html.Span('''In the maps below, we allow the user to
                        select a range of years anfd aggregate the selected indicators
                        for those years. How to use-''')],
                                style={"text-align": "left", "padding-top": 10}
                               ),
                        html.Div([html.Span('''(a) select an indicator from climate parameters''')],
                                style={"text-align": "left", "padding-top": 10}
                               ),
                        html.Div([html.Span('''(b) select an indicator from economic parameters''')],
                                style={"text-align": "left", "padding-top": 10}
                               ),
                        html.Div([html.Span('''(c) select year from the year slider''')],
                                style={"text-align": "left", "padding-top": 10}
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
                                            options=[{'label': "GDP current PPP intl $",
                                                         'value': 'gdp_current'},
                                                    {'label': "GDP per capita (PPP 2017 Intl $)", 'value': 'gdp_capita'},
                                                    {'label': "Exports (constant 2015 US$)", 'value': 'exports_gns'},
                                                    {'label': "Imports (constant 2015 US$)", 'value': 'imports_gns'}]),
                            dcc.Graph(id="econ-map-agg", style={'width': '80vh', 'height': '80vh'})
                            ]),
                            html.Div(className="six columns", 
                            children = [
                            dcc.Dropdown(id="climate-param-agg", value='co2_emissions_kt',
                                            options=[{'label': "C02 emissions(kt)", 'value': 'co2_emissions_kt'},
                                                    {'label': "C02 emissions per capita (metric tons)", 
                                                            'value': 'co2_emissions_capita'},
                                                    {'label': "PM 2.5(mg per cubic meter)", 'value': 'pm_25'},
                                                    {'label': "Greenhouse gases(tons/capita)",
                                                             'value': 'ghg_capita'},
                                                    {'label': "Mean surface temperature (change)",
                                                             'value': 'mean_surface_temp'}]),
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
                                style={"text-align": "left", "padding-top": 10}
                               ),
                        html.Div([html.Span('''How to use- Select range of years by using the 
                            range slider''')],
                                style={"text-align": "left", "padding-top": 10}
                               ),
                        html.Div([html.Span('''
                            In this map, we take the difference of average growth rate between GDP 
                            and Co2 emissions. So for the years selected, we calculate Compounded 
                            Annual Growth Rate (CAGR) for both the indicators and take their 
                            difference. The bigger the size of the bubble, the bigger the 
                            difference between CAGR for the two indicators.''')],
                                style={"text-align": "left", "padding-top": 10}
                               ),
                        html.Div([html.Span('''
                            As we move across time, we can see that the difference between these 
                            CAGR for these two indicators is negative for more countries. Thus, 
                            with time, an increasing number of countries are growing more in 
                            their Co2 emissions as compared to their GDP. This change is more 
                            pronounced in Africa and East Asia. Europe, on the other hand has 
                            positive gdp growth- emission growth difference throughout time. 
                            This means that developing and under developed countries, in their 
                            development phase, produce significantly large emissions. 
                            Developed countries on the other hand grow at a stable rate and do 
                            not emit a lot of emissions.''')],
                                style={"text-align": "left", "padding-top": 10}
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
                        html.Div([html.Span('''In this section, we are regressing log of 
                        Co2 emissions on log gdp and log gdp sqaured. The user can select
                        forest areas as an additional independent variable along with
                        the region they want to see the regressions on. For future iterations 
                        of the project, the model would greatly benefit by incoproating more
                        socio-economic variables like human development index for each country and
                        an indicator on the quality of governance and level of corruption. It would be 
                        interesting to see the inter-play of these socio-economic indicators on the 
                        level of emissions. Additionally, a test to account for the structural 
                        break like the years around major climate conventions would offer meaningful
                        insights on the changes in the level of emissions and if these climatic 
                        conventions have had any impact on the level of emissions. This layer also 
                        has an animated scatter plot that showcases the interaction between the 
                        variables in the benchmark model - log GDP per capita and log CO2 
                        emissions per capita over the given range of years.''')],
                                style={"text-align": "left", "padding-top": 10}
                               ),
                        html.Hr(className='gap'),
                        html.Div(className="row",
                        children = [
                            html.Div(className='row', children=[
                                html.Div(children=[
                                    html.Div(className='four columns', children=[
                                         dcc.Dropdown(id="regions-list", value='Asia',
                                            options=regions_lst(),
                                            style={"width": "100%"})
                                    ]),
                                    html.Div(className='eight columns', children=[
                                         dcc.Dropdown(id="control-vars-list", value='',
                                            options=[{'label': "Forest area", 'value': 'forest_area'}],
                                            multi=True,
                                            style={"width": "100%"})
                                    ])
                                ])
                            ]),
                            html.Hr(className='gap'),
                            html.Div([html.H5("Correlations")],
                                style={'textAlign': "left", "padding-bottom": "50"}
                               ),
                            dcc.Graph(id="scatter-bubble", style={'width': '120vh', 'height': '70vh'}),
                            html.Div([html.H5("Regression summary")],
                                style={'textAlign': "left", "padding-bottom": "50"}
                               ),
                            dash_table.DataTable(id='reg-table',
                                    columns=[
                                            {'name': 'indicators', 'id': 'indicators'},
                                            {'name': 'coefficients', 'id': 'coefficients'},
                                            {'name': 'std_error', 'id': 'std_error'},
                                            {'name': 'p-value', 'id': 'pvalue'}],
                                    style_header={'text-align': 'center'},
                                    style_data={'text-align': 'center'}
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
                          colorscale="RdBu",marker={'line':
                           {'color': 'rgb(180,180,180)','width': 0.5}},
                          colorbar={"thickness": 10,"len": 0.68,"x": 0.98,"y": 0.50})   
    return {"data": [trace],
            "layout": go.Layout(height=700, 
            geo={'showframe': True,'showcoastlines': False, 
                'projection': {'type': "mercator"}},
                margin=dict(l=00, r=200, b=0, t=0))}

@app.callback(
    dash.dependencies.Output("climate-map", "figure"),
    [dash.dependencies.Input("climate-param", "value"),
     dash.dependencies.Input("year-slider", "value")]
)
def update_climate_map(indicator, year):
    print("updating the climate map")
    df = extract_map_data(indicator, "climate_indicators", str(year))
    df["hover_text"] = df["country"] + ": " + df[indicator].apply(str)

    trace = go.Choropleth(locations=df['iso_code'],z=df[indicator],
                          text=df['hover_text'],
                          hoverinfo="text",
                          marker_line_color='white',
                          autocolorscale=False,
                          reversescale=True,
                          colorscale="RdBu",marker={'line':
                           {'color': 'rgb(180,180,180)','width': 0.5}},
                          colorbar={"thickness": 10,"len": 0.80,"x": 0.98,"y": 0.50})   
    return {"data": [trace],
            "layout": go.Layout(height=700,
                        geo={'showframe': True, 'showcoastlines': False,
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
                          colorscale="RdBu",marker={'line':
                           {'color': 'rgb(180,180,180)','width': 0.5}},
                          colorbar={"thickness": 10,"len": 0.68,"x": 0.98,"y": 0.50})   
    return {"data": [trace],
            "layout": go.Layout(height=700, 
                                geo={'showframe': True,'showcoastlines': False,
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
                          colorscale="RdBu",marker={'line': 
                                    {'color': 'rgb(180,180,180)','width': 0.5}},
                          colorbar={"thickness": 10,"len": 0.68,"x": 0.98,"y": 0.50})   
    return {"data": [trace],
            "layout": go.Layout(height=700, 
                                geo={'showframe': True,'showcoastlines': False,
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

    fig = px.scatter(df, x="log_gdp_current", y="log_co2",
            animation_frame="year", animation_group="country",
	         size="population", hover_name="country", size_max=60,
            )
    
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
    reg_df.reset_index(inplace=True)
    reg_df.rename(columns = {'index': 'indicators', 'parameter': 'coefficients'}, inplace=True)
    reg_df['coefficients'] = reg_df['coefficients'].round(decimals = 5)
    reg_df['std_error'] = reg_df['std_error'].round(decimals = 3)
    reg_df['pvalue'] = reg_df['pvalue'].round(decimals = 4)
    
    return reg_df.to_dict('records')


if __name__ == '__main__':
    app.run_server(debug=True, port=8051)


