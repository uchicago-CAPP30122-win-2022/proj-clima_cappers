import requests

# https://api.worldbank.org/v2/country/indicator/SP.POP.TOTL?date=2000:2001

ALL_PARAMETERS = ["EN.ATM.CO2E.PC", "AG.LND.FRST.ZS", "EN.ATM.PM25.MC.M3",
              "EN.ATM.SF6G.KT.CE", "EN.ATM.GHGT.KT.CE" ]

class DataCollector: 

    def __init__(self):
        self.country_client = "https://api.worldbank.org/v2/country?format=json"\
                               "&page=%s"
        self.main_client = "https://api.worldbank.org/v2/country/{country}/"\
                           "indicator/{parameter}?date=1995:2021"


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
            for parameter in ALL_PARAMETERS:
                results = requests.get(self.main_client.format(country = country, 
                                                            parameter = parameter))
                json_data = results.json()
                ## create a dataframe for each country, year, indicator
                ## get the next indicator for this countryy and join it with this dataset
                ## push this dataset where each row is a (country, year, indicator1, i2) tuple
                # to the databse



