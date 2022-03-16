from cmath import exp
import pandas as pd
import sqlite3
import numpy as np
from linearmodels import PanelOLS
from sklearn.impute import KNNImputer
import statsmodels.api as sm

connection = sqlite3.connect("./data/indicators.sqlite3", check_same_thread=False)

def extract_countries(region):
    '''
    '''
    params = [region]
    query = ''' SELECT e.country, e.iso_code, e.year,
                 e.gdp_current, e.population, c.co2_emissions_kt
                 FROM econ_indicators e
                 JOIN climate_indicators c
                 ON e.iso_code = c.iso_code AND e.year = c.year
                 JOIN region_mapping r
                 ON e.iso_code = r.iso_code
                 WHERE r.region = ? AND TRIM(e.population) <> '' '''

    df = pd.read_sql_query(query, connection, params=params)
    df["log_gdp_current"] = np.log(pd.to_numeric(df["gdp_current"]))
    df["log_co2"] = np.log(pd.to_numeric(df["co2_emissions_kt"]))
    return df

def regression_df(controls, region):
    '''
    '''
    params = [region]
    # if isinstance(controls, list):
    #     format_lst = ',' + ','.join(controls)
    # else:
    #     format_lst = controls
    query = ''' SELECT e.country, e.iso_code, e.year,
                 e.gdp_capita, e.imports_gns, e.exports_gns, 
                 c.co2_emissions_kt, c.co2_emissions_capita,   
                 c.forest_area
                 FROM econ_indicators e
                 JOIN climate_indicators c
                 ON e.iso_code = c.iso_code AND e.year = c.year
                 JOIN region_mapping r
                 ON e.iso_code = r.iso_code
                 WHERE r.region = ? '''
    
    data2 = pd.read_sql_query(query, connection, params=params)
    data2.replace('', np.nan, inplace=True)

    # data2 = combined_data.copy()
    data2["log_co2_capita"] = np.log(data2["co2_emissions_capita"])
    data2["log_gdp_capita"] = np.log(pd.to_numeric(data2["gdp_capita"]))
    data2["log_gdp_capita_sq"] = (np.log(pd.to_numeric(data2["gdp_capita"])))**2
    data2["net_exports"] = data2["exports_gns"] - data2["imports_gns"]

    #drop indicators with more than 35% missing values
    data_remove_na = missing_data_prop(data2)

    #drop countries with more than 35% missing values
    drop_countries = []
    for country in data2["iso_code"].unique():
        df = data_remove_na[data_remove_na["iso_code"] == country]
        df_clean = missing_data_prop(df)
        if df.shape[1] != df_clean.shape[1]:
            drop_countries.append(country)

    data2 = data2[data2.iso_code.isin(drop_countries) == False]
    # data2["log_net_exports"] = np.log(data2["net_exports"])

    res = data2.groupby(["iso_code", "country"], 
                         as_index = False).apply(impute_missing_values)
    res.reset_index(drop=True, inplace=True)
    data2.reset_index(drop=True, inplace=True)
    frames = [data2.iloc[:,:3], res]
    imputed_dataset = pd.concat(frames,  axis=1)

    if not isinstance(controls, list):
        if controls:
            exp_vars = [controls]
        else:
            exp_vars = [] 
    else:
        exp_vars = controls

    regression_result = fixed_effects_model(imputed_dataset, exp_vars)

    return regression_result

#############################AUXILARY FUNCTIONS#################################

def missing_data_prop(df):
    '''
    Removes columns in a dataframe with more than 35% missing values.

    Input:
        df(DataFrame): Input dataframe

    Returns:
        df(DataFrame): Updated dataframe
    '''
    perc = 35.0
    min_count =  int(((100-perc)/100)*df.shape[0] + 1)
    df = df.dropna(axis = 1, thresh = min_count)
    return df


def impute_missing_values(df):
    '''
    Impute missing values for the indicators using KNNImputer. 

    Input:
        df(DataFrame): Input dataframe

    Return:
        df(DataFrame): Updated dataframe with all imputed indicators
    '''
    imputer = KNNImputer(n_neighbors=2)
    X = df.iloc[:,3:]
    out = imputer.fit_transform(X)
    out1 = pd.DataFrame(out, columns = df.columns[3:])
    return out1

def fixed_effects_model(dataset, explanatory_variable = None):
    '''
    Run a time fixed effects regression on the given dataset. The benchmark 
    regression model includes log_CO2_emissions as the dependent variable and 
    log_GDP_capita as the independent variable. The user can also run the 
    regression by providing additional expanatory variables. 

    Input:
        dataset ()

    '''
    vars = ["log_gdp_capita", "log_gdp_capita_sq"]
    vars.extend(explanatory_variable)
    exog_vars = vars + np.unique(dataset.year)[1::].tolist()
    dataset['year'] = pd.to_datetime(dataset['year'], format='%Y')
    dataset = dataset.set_index('year', append=True)
    exog = sm.tools.tools.add_constant(dataset.filter(exog_vars, axis = 1))
    endog = dataset["log_co2_capita"]
    mod_fe = PanelOLS(endog, exog, time_effects=True)
    fe_res = mod_fe.fit()
    return fe_res