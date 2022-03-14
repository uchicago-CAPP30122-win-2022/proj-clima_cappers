import sqlite3
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

### NEW LIBRARIES
import matplotlib.pyplot as plt
import seaborn as sns
#Pooled OLS
import statsmodels.api as sm
# FE  model
from linearmodels import PanelOLS
from sklearn.impute import KNNImputer


connection = sqlite3.connect("indicators.sqlite3", check_same_thread=False)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# creating date_dict for year slider

def extract_map_data(indicators, region):
    # params = [indicator, table, year]
    con = sqlite3.connect('indicators.sqlite3')
    climate_data = pd.read_sql_query("SELECT * FROM climate_indicators", con)
    economic_data = pd.read_sql_query("SELECT * FROM econ_indicators", con)
    region_mapping = pd.read_sql_query("SELECT * FROM region_mapping", con)

    merged_dataset = pd.merge(economic_data, climate_data, 
                              on = ["iso_code", "year", "country"], 
                              how = "left")

    #drop indicators with more than 35% missing values
    data_remove_na = missing_data_prop(merged_dataset)

    #drop countries with more than 35% missing values
    drop_countries = []
    for country in combined_data["iso_code"].unique():
        df = data_remove_na[data_remove_na["iso_code"] == country]
        df_clean = missing_data_prop(df)
        if df.shape[1] != df_clean.shape[1]:
            drop_countries.append(country)

    combined_data = combined_data[combined_data.iso_code.isin(drop_countries) == False]

    data2 = combined_data.copy()
    data2["log_ghg_capita"] = np.log(data2["ghg_capita"])
    data2["log_gdp_capita"] = np.log(pd.to_numeric(data2["gdp_capita"]))
    data2["log_gdp_capita_sq"] = (np.log(pd.to_numeric(data2["gdp_capita"])))**2

    res = data2.groupby(["iso_code", "country"], as_index = False).apply(impute_missing_values)
    res.reset_index(drop=True, inplace=True)
    data2.reset_index(drop=True, inplace=True)
    frames = [data2.iloc[:,:3], res]
    imputed_dataset = pd.concat(frames,  axis=1)

    final_dataset = pd.merge(imputed_dataset , region_mapping, 
                             on = [ "iso_code",], how = "left")

    # DECIDE IF THE INPUT WILL BE REGION OR SUB-REGION
    regional_data = final_dataset[final_dataset["region"] == region]

    regression_result = fixed_effects_model(regional_data, indicators)


    ## for the scatter plot, we can log_ghg_capita and log_gpd_capita from 
    ## regional_data

    return regression_result, regional_data 

#############################AUXILARY FUNCTIONS#################################

def missing_data_prop(df):
    perc = 35.0
    min_count =  int(((100-perc)/100)*df.shape[0] + 1)
    df = df.dropna(axis = 1, thresh = min_count)
    return df


def impute_missing_values(df):
    imputer = KNNImputer(n_neighbors=2)
    X = df.iloc[:,3:]
    out = imputer.fit_transform(X)
    out1 = pd.DataFrame(out, columns = df.columns[3:])
    return out1

def fixed_effects_model(dataset, explanatory_variable = None):
    vars = ["log_gdp_capita", "log_gdp_capita_sq"]
    exog_vars = vars.extend(explanatory_variable) + np.unique(dataset.year)[1::].tolist()
    dataset['year'] = pd.to_datetime(dataset['year'], format='%Y')
    dataset = dataset.set_index('year', append=True)
    exog = sm.tools.tools.add_constant(dataset.filter(exog_vars, axis = 1))
    endog = dataset["log_ghg_capita"]
    mod_fe = PanelOLS(endog, exog)
    fe_res = mod_fe.fit()
    return fe_res

#################################################################################
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Climate vs Economy'
app.layout = html.Div([html.Div([html.H1("Climate Change and the Economy")],
                                style={'textAlign': "center", "padding-bottom": "30"}
                               ),
                        html.Div([
                            html.Div([html.Span("Metric to display : ", className="six columns",
                                           style={"text-align": "right", "width": "40%", "padding-top": 10}),
                                 dcc.Dropdown(id="climate-param", value='co2_emissions_capita',
                                              options=[{'label': "CO2 Emissions per capita", 'value': 'co2_emissions_capita'},
                                                       {'label': "Mean Surface Temperature", 'value': 'mean_surface_temp'},
                                                       {'label': "GHG emissions growth", 'value': 'ghg_growth'},
                                                       {'label': "Forest Area", 'value': 'forest_area'}],
                                              style={"display": "block", "margin-left": "auto", "margin-right": "auto",
                                                     "width": "70%"},
                                              className="six columns")], className="row"),
                            html.Div([dcc.Graph(id="climate-map")], className="row"),
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
    dash.dependencies.Output("climate-map", "figure"),
    [dash.dependencies.Input("climate-param", "value"),
     dash.dependencies.Input("year-slider", "value")]
)
def update_figure(indicator, year):
    df = extract_map_data(indicator, "climate_indicators", str(year))

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