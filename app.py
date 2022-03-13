import sqlite3
from turtle import title
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px


connection = sqlite3.connect("indicators.sqlite3", check_same_thread=False)

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

def indicators_lst(lst):
    ind_lst= []
    for label, value in lst:
        ind_dict = {}
        ind_dict['label'] = label
        ind_dict['value'] = value
        ind_lst.append(ind_dict)
    return ind_lst

def country_lst():
    query = ''' SELECT DISTINCT country, iso_code FROM econ_indicators '''
    df = pd.read_sql_query(query, connection)
    country_lst= []
    for i, row in df.iterrows():
        country_dict = {}
        country_dict['label'] = row['country']
        country_dict['value'] = row['iso_code']
        country_lst.append(country_dict)
    return country_lst

def extract_map_data(indicator, table, year):
    # params = [indicator, table, year]
    query = ''' SELECT country, iso_code, {} FROM {} WHERE year = {} '''. \
                format(indicator, table, year)
    df = pd.read_sql_query(query, connection)
    return df

def extract_bar_data(indicator, table, year):
    query = ''' SELECT country, iso_code, {} FROM {} 
                WHERE year = {} AND TRIM({}) <> '' AND iso_code <> 'WLD'
                ORDER BY {} DESC LIMIT 5 '''. \
                format(indicator, table, year, indicator, indicator)
    df = pd.read_sql_query(query, connection)
    return df

def trend_df(indicator_lst, country):
    params = [country]
    # braces = ','.join(len(indicator_lst) * '{}')
    # print("indicator list is:", indicator_lst)
    if isinstance(indicator_lst, list):
        format_lst = ','.join(indicator_lst)
    else:
        format_lst = indicator_lst
    print(format_lst)
    query = ''' SELECT e.iso_code, e.year, ''' + format_lst + ''' FROM econ_indicators e
                 JOIN climate_indicators c
                 ON e.iso_code = c.iso_code AND e.year = c.year
                 WHERE e.iso_code = ? '''
    df = pd.read_sql_query(query, connection, params=params)
    df = pd.melt(df, id_vars=['iso_code', 'year'], value_vars=df.columns[2:],
                  var_name='indicators', value_name='value')
    return df

def extract_bubble_data(year_input):
    
    query1 = ''' SELECT country, iso_code, gdp_current FROM econ_indicators WHERE year BETWEEN {} AND {}'''. \
                format(year_input[0], year_input[1])
    
    query2 = ''' SELECT country, iso_code, co2_emissions_kt FROM climate_indicators WHERE year BETWEEN {} AND {}'''. \
                format(year_input[0], year_input[1])
    
    df_econ = pd.read_sql_query(query1, connection)
    df_climate = pd.read_sql_query(query2, connection)
    print("climate df is", df_climate)
    df_econ['gdp_current'] = pd.to_numeric(df_econ['gdp_current'], downcast="float")
    df_climate['co2_emissions_kt'] = pd.to_numeric(df_climate['co2_emissions_kt'], downcast="float")

    df_econ_agg= aggregate_weight(df_econ, 'gdp_current')
    df_climate_agg= aggregate_weight(df_climate, 'co2_emissions_kt')
    df_climate_agg= df_climate_agg.drop('country', axis=1)
    merge_econ_climate = pd.merge(df_econ_agg, df_climate_agg, how= "left", on=["iso_code"])
    nan_values = merge_econ_climate[merge_econ_climate.isna().any(axis=1)]
    merge_econ_climate.dropna(axis=0, how='any', thresh=None, subset=None, inplace=True)
    merge_econ_climate['difference'] = abs(merge_econ_climate['gdp_current'] - merge_econ_climate['co2_emissions_kt'])*1000
    merge_econ_climate= merge_econ_climate.append(nan_values)
    merge_econ_climate= merge_econ_climate.drop(['gdp_current', 'co2_emissions_kt'], axis=1)
    merge_econ_climate.dropna(axis=0, how='any', inplace=True)

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
    print("df_new is", df_new)
    return df_new


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
                        html.Div([html.H3("Comparing indicators")],
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
                                         dcc.Dropdown(id="multi-params", value='gdp_constant_change',
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
                        dcc.Graph(id="bubble-chart")
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
    print("bubble df is", df)

    fig = px.scatter_geo(df, locations="iso_code",
                     hover_name="country", size="difference",
                     projection="natural earth")
    
    return fig


if __name__ == '__main__':
    app.run_server(debug=True, port=8053)


