import pandas as pd
import numpy as np
import sqlite3

connection = sqlite3.connect("./data/indicators.sqlite3", check_same_thread=False)

def extract_agg_data(indicator, table, year_input):
    """
    This function aggegates the selected indicator for a range of years

    Arguments
    --------------
    indicator- str
              the name of the indicator that the user selects on the page
    table- str
            the name of the table that we will be querying the data from
    year_input- list
            the list with start and end year

    Returns
    -------------
    df_agg- pandas dataframe
            pandas dataframe that contains the indicator aggregated for multiple
            years
    """
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
    """
    This function takes the simple average of the indicator

    Arguments
    ---------------
    df: pandas dataframe
        the dataframe that contains the value of an indicator for the selected
        years
    indicator- str
        the name of the indicator

    Returns
    --------------
    df_new- pandas dataframe
        the dataframe that contains the indicator value averaged for each country
    """
    df_new= df.groupby(['country','iso_code'], as_index=False).mean()
    df_new.rename(columns = {None: indicator}, inplace = True)
    return df_new

def w_avg_1(df_weigh, values, weights):
    """
    This function calculate 

    Arguments
    ---------------
    df_weigh: pandas dataframe
        the dataframe that contains the value of an indicator for the selected
        years for a country
    values- str
        the name of the indicator for which we want take the average
    weights- str
        the name of the indicator by which we want to weigh the value

    Returns
    --------------
    float
        the value for each country
    """
    d = df_weigh[values]
    w = df_weigh[weights]
    return (d * w).sum() / w.sum()

def aggregate_weight_1(df_get, indicator):
    """
    This function calculates the weighted average for each country.

    Arguments
    ---------------
    df_weigh: pandas dataframe
        the dataframe that contains the value of an indicator for the selected
        years
    values- str
        the name of the indicator for which we want take the average
    weights- str
        the name of the indicator by which we want to weigh the value

    Returns
    --------------
    df_new- pandas datafram
        the dataframe that contains the indicator value averaged for each country
    """
    df_new= df_get.groupby(['iso_code', 'country'], as_index=False).apply(w_avg_1, indicator, 
                                                                            'population')
    df_new.rename(columns = {None: indicator}, inplace = True)
    return df_new
