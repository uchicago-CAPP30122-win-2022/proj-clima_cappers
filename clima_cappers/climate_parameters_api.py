import requests
import pandas as pd
import sqlite3


# connecting to the sqlite3 db
connection = sqlite3.connect("data/indicators.sqlite3")
c = connection.cursor()

#mean surface temperature data
mst = pd.read_csv("data/mean_st_output.csv")
mst.drop(["Country"], axis = 1, inplace = True)
mst.rename(columns={"ISO3": "Country_code"}, inplace = True)

# parameterized sql query for db insert
sql_insert = '''INSERT INTO climate_indicators VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?,
                 ?,n? ,?, ?, ?, ?, ?, ?, ?, ?,?)''' 


ALL_PARAMETERS = ["EN.ATM.CO2E.KT", "EN.ATM.CO2E.PC", "AG.LND.FRST.ZS",
                  "SP.POP.TOTL", "EG.ELC.HYRO.ZS", "EG.ELC.NGAS.ZS", 
                  "EG.ELC.NUCL.ZS","EG.ELC.PETR.ZS", "EG.ELC.COAL.ZS", 
                  "EG.ELC.FOSL.ZS", "EG.ELC.RNWX.ZS","EN.ATM.PM25.MC.M3", 
                  "EN.ATM.SF6G.KT.CE", "EN.ATM.GHGT.KT.CE", "CC.GHG.GRPE", 
                  "CC.GHG.PECA"]

class DataCollector: 

    def __init__(self):
        '''
        Constructor for the DataCollector class.
        '''
        self.country_client = "https://api.worldbank.org/v2/country?format=json"\
                               "&page=%s"

        self.main_client = "https://api.worldbank.org/v2/country/{country}/"\
                           "indicator/{parameter}?date=1995:2021&format=json"


    def find_countries(self):
        '''
        Returns the list of all countries on the world bank database.

        Returns: 
                all_countries (list): a list of tuples with country name and 
                                      country iso3 codes.
        '''
        countries = []
        for page in range(1,7):
            results = requests.get(self.country_client%page)
            json_data = results.json()
            dict_countries = json_data[1]
            for d in dict_countries:
                countries.append((d["name"], d["id"]))
        return countries


    def get_data(self):
        '''
        For each country, gets the data from the World Bank API and creates a 
        dataframe with all indicators over the selected range of years. 
        Convert each row of the database into tuples and write it to the sql
        database. Repeat the process for all the countries. At the end of the
        process, the climate_indicators table in the database is populated.
        '''
        all_countries = self.find_countries()
        check = set()
        for name, code in all_countries:
            print("Currently in country:", name)
            country_table = {"Country": [name] * 26, "Country_code": [code]*26, 
                    "Year": [i for i in (range(1995, 2021))]}
            data = pd.DataFrame(country_table)
            i = 0
            for i in range(len(ALL_PARAMETERS)):
                parameter = ALL_PARAMETERS[i]
                print("Currently in indicator", parameter, "for country", name)
                results = requests.get(self.main_client.format(country = code, 
                                                            parameter = parameter))
                data[parameter] = None
                try:
                    indicator_data_dicts = results.json()[1]
                    i += 1
                except:
                    print("JSONDecodeError. Begin again with the same country.")
                    continue
                if indicator_data_dicts:
                    for x in indicator_data_dicts:
                        data.loc[data.Year == int(x["date"]), parameter] = x["value"]  
            check.add(code)
            data= data.merge(mst, on=["Country_code", "Year"])
            data_tuples = data.apply(tuple, axis=1).tolist()
            print("Writing data for", name,  "into the database")
            try:
                c.executemany(sql_insert, data_tuples)
            except:
                print("Data already exists. Moving on to the next iteration.")
                continue
            connection.commit()    
        connection.close()


if __name__ == '__main__':
    obj = DataCollector()
    obj.get_data()