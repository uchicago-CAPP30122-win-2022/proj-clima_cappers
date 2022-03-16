import pandas as pd
import sqlite3
import numpy as np
from linearmodels import PanelOLS
from sklearn.impute import KNNImputer
import statsmodels.api as sm

connection = sqlite3.connect("./data/indicators.sqlite3", check_same_thread=False)

def extract_countries(region):
    params = [region]
    query = ''' SELECT e.country, e.iso_code, e.year,
                 e.gdp_current, e.population, c.ghg_total
                 FROM econ_indicators e
                 JOIN climate_indicators c
                 ON e.iso_code = c.iso_code AND e.year = c.year
                 JOIN region_mapping r
                 ON e.iso_code = r.iso_code
                 WHERE r.sub_region = ? AND TRIM(e.population) <> '' '''
    df = pd.read_sql_query(query, connection, params=params)
    df["log_gdp_current"] = np.log(pd.to_numeric(df["gdp_current"]))
    df["log_ghg_total"] = np.log(pd.to_numeric(df["ghg_total"]))
    return df

def regression_df(controls, region):
    params = [region]
    if isinstance(controls, list):
        format_lst = ',' + ','.join(controls)
    else:
        format_lst = controls
    query = ''' SELECT e.country, e.iso_code, e.year,
                 e.gdp_capita, c.ghg_capita ''' \
                 + format_lst + \
                 '''
                 FROM econ_indicators e
                 JOIN climate_indicators c
                 ON e.iso_code = c.iso_code AND e.year = c.year
                 JOIN region_mapping r
                 ON e.iso_code = r.iso_code
                 WHERE r.sub_region = ? '''
    
    merged_dataset = pd.read_sql_query(query, connection, params=params)
    merged_dataset.replace('', np.nan, inplace=True)

    #drop indicators with more than 35% missing values
    data_remove_na = missing_data_prop(merged_dataset)

    #drop countries with more than 35% missing values
    drop_countries = []
    for country in merged_dataset["iso_code"].unique():
        df = data_remove_na[data_remove_na["iso_code"] == country]
        df_clean = missing_data_prop(df)
        if df.shape[1] != df_clean.shape[1]:
            drop_countries.append(country)

    combined_data = merged_dataset[merged_dataset.iso_code.isin(drop_countries) == False]

    data2 = combined_data.copy()
    data2["log_ghg_capita"] = np.log(data2["ghg_capita"])
    data2["log_gdp_capita"] = np.log(pd.to_numeric(data2["gdp_capita"]))
    data2["log_gdp_capita_sq"] = (np.log(pd.to_numeric(data2["gdp_capita"])))**2

    res = data2.groupby(["iso_code", "country"], as_index = False).apply(impute_missing_values)
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
    vars.extend(explanatory_variable)
    exog_vars = vars + np.unique(dataset.year)[1::].tolist()
    dataset['year'] = pd.to_datetime(dataset['year'], format='%Y')
    dataset = dataset.set_index('year', append=True)
    exog = sm.tools.tools.add_constant(dataset.filter(exog_vars, axis = 1))
    endog = dataset["log_ghg_capita"]
    mod_fe = PanelOLS(endog, exog)
    fe_res = mod_fe.fit()
    return fe_res