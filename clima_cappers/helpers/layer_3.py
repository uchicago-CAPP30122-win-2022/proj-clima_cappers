import pandas as pd
import numpy as np
import sqlite3

connection = sqlite3.connect("./data/indicators.sqlite3", check_same_thread=False)

def extract_bubble_data(year_input):
    
    query1 = ''' SELECT country, iso_code, gdp_current FROM econ_indicators WHERE year BETWEEN {} AND {}'''. \
                format(year_input[0], year_input[1])
    
    query2 = ''' SELECT country, iso_code, co2_emissions_kt FROM climate_indicators WHERE year BETWEEN {} AND {}'''. \
                format(year_input[0], year_input[1])
    
    df_econ = pd.read_sql_query(query1, connection)
    df_climate = pd.read_sql_query(query2, connection)
    df_econ['gdp_current'] = pd.to_numeric(df_econ['gdp_current'], downcast="float")
    df_climate['co2_emissions_kt'] = pd.to_numeric(df_climate['co2_emissions_kt'], downcast="float")

    df_econ_agg= aggregate_weight_2(df_econ, 'gdp_current')
    df_climate_agg= aggregate_weight_2(df_climate, 'co2_emissions_kt')
    df_climate_agg= df_climate_agg.drop('country', axis=1)
    merge_econ_climate = pd.merge(df_econ_agg, df_climate_agg, how= "left", on=["iso_code"])
    nan_values = merge_econ_climate[merge_econ_climate.isna().any(axis=1)]
    merge_econ_climate.dropna(axis=0, how='any', thresh=None, subset=None, inplace=True)
    merge_econ_climate['difference'] = merge_econ_climate['gdp_current'] - merge_econ_climate['co2_emissions_kt']

    merge_econ_climate["sign"]= np.sign(merge_econ_climate["difference"])
    merge_econ_climate['net_growth_rate'] = merge_econ_climate["sign"]
    merge_econ_climate.loc[merge_econ_climate['sign'] == 1, 'net_growth_rate'] = 'Positive Growth-Emission Difference'
    merge_econ_climate.loc[merge_econ_climate['sign'] == 0, 'net_growth_rate'] = 'Positive Growth-Emission Difference'
    merge_econ_climate.loc[merge_econ_climate['sign'] == -1, 'net_growth_rate'] = 'Negative Growth-Emission Difference'

    merge_econ_climate= merge_econ_climate.append(nan_values)
    merge_econ_climate= merge_econ_climate.drop(['gdp_current', 'co2_emissions_kt'], axis=1)
    merge_econ_climate.dropna(axis=0, how='any', inplace=True)
    merge_econ_climate['difference'] = abs(merge_econ_climate['difference'])*1000

    return merge_econ_climate

def w_avg_2(df_weigh, values):
    d = df_weigh[values]
    last= d.iloc[-1]
    first= d.iloc[0]
    
    if pd.isna(first) or pd.isna(last):
        return np.NaN
    else:
        ratio= (last/first)**(1/len(d))-1
        return ratio

def aggregate_weight_2(df_get, indicator):
    df_new= df_get.groupby(['iso_code', 'country'], as_index=False).apply(w_avg_2, indicator)
    df_new.rename(columns = {None: indicator}, inplace = True)
    return df_new