import requests
import pandas as pd

# https://api.worldbank.org/v2/country/indicator/SP.POP.TOTL?date=2000:2001

ALL_PARAMETERS = ["EN.ATM.CO2E.PC", "AG.LND.FRST.ZS", "EN.ATM.PM25.MC.M3",
              "EN.ATM.SF6G.KT.CE", "EN.ATM.GHGT.KT.CE" ]

class DataCollector: 

    def __init__(self):
        self.country_client = "https://api.worldbank.org/v2/country?format=json"\
                               "&page=%s"
        self.main_client = "https://api.worldbank.org/v2/country/{country}/"\
                           "indicator/{parameter}?date=1995:2021&format=json"


    def find_countries(self):
        countries = []
        for page in range(1,7):
            results = requests.get(self.country_client%page)
            json_data = results.json()
            dict_countries = json_data[1]
            for d in dict_countries:
                countries.append(d["id"])
        return countries



    def get_data(self):
        all_countries = self.find_countries()
        for country in all_countries:
            d = {"Country": [country]*26, "Year": [i for i in reversed(range(1995, 2022))]}
            data = pd.DataFrame(d)
            for parameter in ALL_PARAMETERS:
                results = requests.get(self.main_client.format(country = country, 
                                                            parameter = parameter))
                json_data = results.json()
                indicator_name = json_data[1][0]["indicator"]["value"]
                data[indicator_name] = None
                indicator_data_dicts = results.json()[1]
                for d in indicator_data_dicts:
                    data.loc[data.Year == int(d["date"]), indicator_name] = d["value"]
            data_tuples = data.apply(tuple, axis=1).tolist()
            return data




                

                # data = pd.DataFrame(list(results.json()[1].items()),
                #                          columns = ['column1','column2'])

                ## create a dataframe for each country, year, indicator
                ## get the next indicator for this countryy and join it with this dataset
                ## push this dataset where each row is a (country, year, indicator1, i2) tuple
                # to the databse



