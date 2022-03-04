from argparse import _CountAction
from inspect import Parameter
from matplotlib.style import library
from sodapy import Socrata
import requests


# def _decode_libray_data(dct):
#     #First check that all required attributes are inside the dictionary 
#     if all (key in dct for key in ["name_","location","address"]):
#         return Library(dct["name_"],(dct["location"]['latitude'],dct["location"]['longitude']) ,dct["address"])
#     return dct

# https://api.worldbank.org/v2/country/indicator/SP.POP.TOTL?date=2000:2001

ALL_PARAMETERS = ["EN.ATM.CO2E.PC", "AG.LND.FRST.ZS", "EN.ATM.PM25.MC.M3",
              "EN.ATM.SF6G.KT.CE", "EN.ATM.GHGT.KT.CE" ]

class DataCollector: 

    def __init__(self):
        # Unauthenticated client only works with public data sets. Note 'None'
        # in place of application token, and no username or password:
        self.country_client = "https://api.worldbank.org/v2/country?format=json&page=%s"
        
        #second client for country
        self.main_client = "https://api.worldbank.org/v2/{country}/indicator/{parameter}?date=1995:2020"


    def find_countries(self):
        countries = []
        for page in range(1,7):
            results = requests.get(self.country_client%page)
            json_data = results.json()
            dict_countries = json_data[1]
            for d in dict_countries:
                # check1 = d.get("iso2Code", "NA")
                # check2 = d.get("iso2code", "NA")    
                # # if not d.get("iso2Code", "NA") and d.get("iso2code", "NA"):
                # if check1 != "NA" and check2 != "NA":
                #     print(d["id"])
                countries.append(d["id"])
        return countries

    def get_data(self):
        all_countries = self.find_countries()
        for country in all_countries:
            for parameter in ALL_PARAMETERS:
                results = requests.get(self.main_client.format(country, parameter))
                



    # def find_indicators(self, limit):
    #     libraries = []
    #     results = self.client.get("x8fc-8rcq",limit=limit)
    #     for lib_dict in results: 
    #         library = _decode_libray_data(lib_dict)
    #         libraries.append(library)

    #     return libraries


