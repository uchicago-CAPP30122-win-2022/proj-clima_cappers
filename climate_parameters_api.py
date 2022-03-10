import requests
import pandas as pd
import sqlite3

# https://api.worldbank.org/v2/country/indicator/SP.POP.TOTL?date=2000:2001

# connecting to the sqlite3 db
connection = sqlite3.connect("indicators.sqlite3")
c = connection.cursor()

# parameterized sql query for db insert
sql_insert = '''INSERT INTO climate_indicators VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ? ,?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''' 


# to be removed in final draft
sql_distinct = "SELECT DISTINCT(iso_code) FROM climate_indicators"
distinct_codes = c.execute(sql_distinct).fetchall()

ALL_PARAMETERS = ["NY.GDP.PCAP.CD", "SI.POV.GINI", "EN.ATM.CO2E.KT", "EN.ATM.CO2E.PC", 
                  "AG.LND.FRST.ZS","SP.POP.TOTL", "EG.ELC.HYRO.ZS", "EG.ELC.NGAS.ZS", 
                  "EG.ELC.NUCL.ZS","EG.ELC.PETR.ZS", "EG.ELC.COAL.ZS", "EG.ELC.FOSL.ZS", 
                  "EG.ELC.RNWX.ZS","EN.ATM.PM25.MC.M3", "EN.ATM.SF6G.KT.CE", 
                  "EN.ATM.GHGT.KT.CE", "CC.GHG.GRPE", "SI.POV.GINI", "CC.GHG.PECA", 
                  "NE.EXP.GNFS.KD", "NE.IMP.GNFS.KD"]

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
                countries.append((d["name"], d["id"]))
        return countries


    def get_data(self):
        all_countries = self.find_countries()
        print("beginning indicator data extraction")
        for name, code in all_countries:
            if (code,) in distinct_codes and code != "SSF": # "TCA" "ROU": #"MEX" "EST" "FSM" "ITA": #and code != "BRA" and code != "CAN" and code != "ERI": # switzerland
                continue
            print("currently in country", name)
            d = {"Country": [name]*26, "Country_code": [code]*26, 
                    "Year": [i for i in reversed(range(1995, 2021))]}
            data = pd.DataFrame(d)
            for parameter in ALL_PARAMETERS:
                print("currently in indicator", parameter, "for", name)
                results = requests.get(self.main_client.format(country = code, 
                                                            parameter = parameter))
                data[parameter] = None
                # json_data = results.json()
                # indicator_name = json_data[1][0]["indicator"]["value"]
                # data[indicator_name] = None
                indicator_data_dicts = results.json()[1]
                if indicator_data_dicts:
                    for d in indicator_data_dicts:
                        data.loc[data.Year == int(d["date"]), parameter] = d["value"]
            data_tuples = data.apply(tuple, axis=1).tolist()
            print("writing data for", name, "into the db")
            try:
                c.executemany(sql_insert, data_tuples)
            except:
                print("Data already exists. Moving on to the next iteration.")
                continue
            connection.commit()
        connection.close()

        


if __name__ == "__main__":
    obj = DataCollector()
    obj.get_data()



