import pandas as pd
import sqlite3

connection = sqlite3.connect("./data/indicators.sqlite3", check_same_thread=False)


def indicators_lst(lst):
    """
    This function returns a list of dictionaries of both climate and 
    economic indicators transformed to a format compatible with the Dash UI.

    Arguments
    --------------
    lst- list
            the raw list of indicators from the database

    Returns
    -------------
    ind_lst- list
            the list of dictionaries containing the indicators 
            in a Dash compatible format.
    """
    ind_lst= []
    for label, value in lst:
        ind_dict = {}
        ind_dict['label'] = label
        ind_dict['value'] = value
        ind_lst.append(ind_dict)
    return ind_lst


def country_lst():
    """
    This function returns a list of dictionaries of country names
    transformed to a format compatible with the Dash UI.

    Arguments
    --------------
    None

    Returns
    -------------
    country_lst- list
            the list of dictionaries containing the country names 
            in a Dash compatible format.
    """
    query = ''' SELECT DISTINCT country, iso_code FROM econ_indicators '''
    df = pd.read_sql_query(query, connection)
    country_lst= []
    for i, row in df.iterrows():
        country_dict = {}
        country_dict['label'] = row['country']
        country_dict['value'] = row['iso_code']
        country_lst.append(country_dict)
    return country_lst

def regions_lst():
    """
    This function returns a list of dictionaries of region names
    transformed to a format compatible with the Dash UI.

    Arguments
    --------------
    None

    Returns
    -------------
    regions_lst- list
            the list of dictionaries containing the regions
            in a Dash compatible format.
    """
    query = ''' SELECT DISTINCT region FROM region_mapping '''
    df = pd.read_sql_query(query, connection)
    regions_lst = []
    for _, row in df.iterrows():
        regions_dict = {}
        regions_dict['label'] = row['region']
        regions_dict['value'] = row['region']
        regions_lst.append(regions_dict)
    return regions_lst