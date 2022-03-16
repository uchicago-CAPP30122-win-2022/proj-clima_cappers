import pandas as pd
import numpy as np
import sqlite3

connection = sqlite3.connect("./data/indicators.sqlite3", check_same_thread=False)


def extract_map_data(indicator, table, year):
    """
    This function returns the selected indicator for a given year.

    Arguments
    --------------
    indicator- str
              the name of the indicator that the user selects on the page
    table- str
            the name of the table that we will be querying the data from
    year- str
            the selected year

    Returns
    -------------
    df- pandas dataframe
            pandas dataframe that contains the indicator for the
            given year
    """
    query = ''' SELECT country, iso_code, {} FROM {} WHERE year = {} '''. \
                format(indicator, table, year)
    df = pd.read_sql_query(query, connection)
    return df


def extract_bar_data(indicator, table, year):
    """
    This function returns the top 5 countries for a selected
    indicator for a given year.

    Arguments
    --------------
    indicator- str
              the name of the indicator that the user selects on the page
    table- str
            the name of the table that we will be querying the data from
    year- str
            the selected year

    Returns
    -------------
    df- pandas dataframe
            pandas dataframe that contains the top 5 countries for a 
            selected indicator for the given year
    """
    query = ''' SELECT country, iso_code, {} FROM {} 
                WHERE year = {} AND TRIM({}) <> '' AND iso_code <> 'WLD'
                ORDER BY {} DESC LIMIT 5 '''. \
                format(indicator, table, year, indicator, indicator)
    df = pd.read_sql_query(query, connection)
    return df


def trend_df(indicator_lst, country):
    """
    This function returns the indicators selected for comparison
    for a specific country chosen by the user.

    Arguments
    --------------
    indicator_lst- list
              the list of indicator chosen for comparison by the user
    country- str
            the selected country

    Returns
    -------------
    df- pandas dataframe
            pandas dataframe that contains the indicators for the
            selected country 
    """
    params = [country]
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
