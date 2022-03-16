import pandas as pd
import numpy as np
import sqlite3

connection = sqlite3.connect("clima_cappers/data/indicators.sqlite3", check_same_thread=False)

def extract_agg_data(indicator, table, year_input):
    print("year input type is", type(year_input))
    indicator_agg_simpavg= ["mean_surface_temp",
                            "co2_emissions_kt",
                            "pm_25",
                            "exports_gns",
                            "imports_gns",
                            "gdp_current",
                            ]
    
    indicator_agg_weigh= ['co2_emissions_capita',
                        'ghg_capita',
                        'gdp_capita']
    if indicator in indicator_agg_simpavg:
        query = ''' SELECT country, iso_code, {} FROM {} WHERE year BETWEEN {} AND {}'''. \
                    format(indicator, table, year_input[0], year_input[1])
        df_get = pd.read_sql_query(query, connection)
        df_get[indicator] = pd.to_numeric(df_get[indicator], downcast="float")
        df_agg= aggregate_simple_average(df_get, indicator)
    
    if indicator in indicator_agg_weigh:
        query = ''' SELECT population, country, iso_code, {} FROM {} WHERE year BETWEEN {} AND {}'''. \
                    format(indicator, table, year_input[0], year_input[1])
        print("running the query", query)
        df_get = pd.read_sql_query(query, connection)
        df_get[indicator] = pd.to_numeric(df_get[indicator], downcast="float")
        df_get['population'] = pd.to_numeric(df_get['population'], downcast="float")
        df_agg= aggregate_weight_1(df_get, indicator)
    return df_agg

def aggregate_simple_average(df, indicator):
    df_new= df.groupby(['country','iso_code'], as_index=False).mean()
    df_new.rename(columns = {None: indicator}, inplace = True)
    return df_new

def w_avg_1(df_weigh, values, weights):
    d = df_weigh[values]
    w = df_weigh[weights]
    return (d * w).sum() / w.sum()

def aggregate_weight_1(df_get, indicator):
    df_new= df_get.groupby(['iso_code', 'country'], as_index=False).apply(w_avg_1, indicator, 'population')
    df_new.rename(columns = {None: indicator}, inplace = True)
    return df_new
