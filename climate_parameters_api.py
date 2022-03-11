import requests
import pandas as pd
import sqlite3


# connecting to the sqlite3 db
connection = sqlite3.connect("indicators.sqlite3")
c = connection.cursor()

#mean srface temperature datta
mst = pd.read_csv("mean_st_output.csv")
mst.drop(["Country"], axis = 1, inplace = True)
mst.rename(columns={"ISO3": "Country_code"}, inplace = True)

# parameterized sql query for db insert
sql_insert = '''INSERT INTO climate_indicators VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ? ,?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''' 


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
        for name, code in all_countries:
            if (code,) in distinct_codes and code != "SVK": # and code != "SSF": # "TCA" "ROU": #"MEX" "EST" "FSM" "ITA": #and code != "BRA" and code != "CAN" and code != "ERI": # switzerland
                continue
            print("currently in country", name, code)
            country_table = {"Country": [name] * 26, "Country_code": [code]*26, 
                    "Year": [i for i in (range(1995, 2021))]}
            data = pd.DataFrame(country_table)
            for parameter in ALL_PARAMETERS:
                print("currently in indicator", parameter, "for", name)
                results = requests.get(self.main_client.format(country = code, 
                                                            parameter = parameter))
                data[parameter] = None
                indicator_data_dicts = results.json()[1]
                if indicator_data_dicts:
                    for x in indicator_data_dicts:
                        data.loc[data.Year == int(x["date"]), parameter] = x["value"]
            data= data.merge(mst, on=["Country_code", "Year"])
            print("data", data)
            print("data columns", data.columns)
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



