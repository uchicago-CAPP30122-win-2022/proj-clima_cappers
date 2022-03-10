import sqlite3
import dash
import dash_core_components as dcc
import dash_html_components as html
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

def extract_map_data(indicator, table, year_input):
    params = [indicator, table, year]
    query = ''' SELECT country, iso_code, {} FROM {} WHERE year BETWEEN {} AND {}'''. \
                format(indicator, table, year_input[0], year_input[1])
    print("running the query", query)
    df = pd.read_sql_query(query, connection)
    indicator_agg_simpavg= ["mean_surface_temp",
                            "co2_emissions_kt",
                            "pm_25",
                            "exports_gns",
                            "imports_gns",
                            "gdp_current",
                            ]
    
    if indicator in indicator_agg_simpavg:
        aggregate_simple_average(df)
    print("dataframe is", df)
    return df

def aggregate_simple_average(df):
    pass

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Climate vs Economy'
app.layout = html.Div([html.Div([html.H1("Climate Change and the Economy")],
                                style={'textAlign': "center", "padding-bottom": "30"}
                               ),
                        html.Div([
                            html.Div([html.Span("Metric to display : ", className="six columns",
                                           style={"text-align": "right", "width": "40%", "padding-top": 10}),
                                 dcc.Dropdown(id="econ-param", value='gdp',
                                              options=[{'label': "GDP", 'value': 'gdp'},
                                                       {'label': "GDP per capita", 'value': 'gdp_capita'},
                                                       {'label': "Volume of imports", 'value': 'vol_imports'},
                                                       {'label': "Volume of exports", 'value': 'vol_exports'}],
                                              style={"display": "block", "margin-left": "auto", "margin-right": "auto",
                                                     "width": "70%"},
                                              className="six columns")], className="row"),
                            html.Div([dcc.Graph(id="econ-map")], className="row"),
                            html.Div([dcc.Slider(1995, 2021,
                                        step=None,
                                        marks=date_dict,
                                        value=2002,
                                        id='year-slider')], className="row")
                                ], className="container"),
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
     dash.dependencies.Input("year-slider", "value")]
)
def update_figure(indicator, year):
    df = extract_map_data(indicator, "econ_indicators", str(year))

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
    app.run_server(debug=True)