import pandas as pd
import numpy as np
filename = "C:/Users/dhruv/Desktop/CS Project/weo2021.csv"

df = pd.read_csv(filename)


subject_descriptor_list= ["Gross domestic product, constant prices",
                          "Gross domestic product per capita, constant prices",
                          "Volume of imports of goods and services",
                          "Volume of exports of goods and services",
                          "Population",
                          "Gross domestic product, current prices"]

units_list=["Percent change",
            "Purchasing power parity; 2017 international dollar",
            "Persons",
            "Purchasing power parity; international dollars"]

df_new= df.loc[(df['Subject Descriptor'].isin(subject_descriptor_list) &
        df['Units'].isin(units_list))]

df_new= df_new.drop(["WEO Country Code",
                     "WEO Subject Code",
                     "Country/Series-specific Notes",
                     "Subject Notes",
                     "Units",
                     "Scale",
                     "Country/Series-specific Notes",
                     "Estimates Start After"
                     ], axis=1)
year_to_remove=[]

for year in range (1980, 1995):
    year_to_remove.append(str(year))

df_new= df_new.drop(year_to_remove, axis=1)
years_needed=[]
for year in range (1995,2027):
    years_needed.append(str(year))
    
    
subject_descriptor_list= ["Gross domestic product, constant prices"]
df_one= df_new.loc[(df_new['Subject Descriptor'].isin(subject_descriptor_list))]
df_one_long= pd.melt(df_one, id_vars=['Country', "ISO"], 
                         value_vars= years_needed,
                         var_name= "Year",
                         value_name= "GDP_constant_change")
subject_descriptor_list_new= [
                          "Gross domestic product per capita, constant prices",
                          "Volume of imports of goods and services",
                          "Volume of exports of goods and services",
                          "Population",
                          "Gross domestic product, current prices"]

list_short=["GDP_capita", "vol_imports_change", "vol_exports_change", 
            "Population", "GDP_current"]
for count, value in enumerate(subject_descriptor_list_new):
    l=[value]
    name= list_short[count]
    df_del= df_new.loc[(df_new['Subject Descriptor'].isin(l))]
    df_long= pd.melt(df_del, id_vars=['Country', "ISO"], 
                         value_vars= years_needed,
                         var_name= "Year",
                         value_name= name)
    df_long=df_long[[name]]
    df_one_long= pd.concat([df_one_long, df_long], axis=1, sort= False)

convert_dict = {"GDP_constant_change": float,
                "GDP_capita": float,
                "vol_imports_change": float,
                "vol_exports_change": float,
                "Population": float,
                "GDP_current": float} 

df_one_long['GDP_capita']=df_one_long['GDP_capita'].str.replace(',','')
df_one_long= df_one_long.replace('--', np.nan, regex=True)
df_one_long= df_one_long.replace(',', '', regex=True)
df_one_long = df_one_long.astype(convert_dict) 
df_one_long.to_csv('C:/Users/dhruv/Desktop/CS Project/econ_parameters_out_without_header.csv', index= False, header= False)  