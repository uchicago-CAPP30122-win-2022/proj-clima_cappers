import pandas as pd
import numpy as np
filename = "../data/energy_import_export.csv"


df = pd.read_csv(filename)

l= df.columns
col_year_new_names=[]
col_year_old_names=[]


for ind in range(3):
    col_name= l[ind]
    col_year_new_names.append(col_name)
    col_year_old_names.append(col_name)

for ind in range(3,64):
    col_name= l[ind]
    a= col_name.split()
    new= a[0]
    old= a[1]
    col_year_new_names.append(new)
    col_year_old_names.append(col_name)
    

df=df.set_axis(col_year_new_names, axis=1)

df['Series Name'] = df['Series Name'].replace(['Imports of goods and services (constant 2015 US$)'],'imports_gns')
df['Series Name'] = df['Series Name'].replace(['Exports of goods and services (constant 2015 US$)'],'exports_gns')

df['Series Name'] = df['Series Name'].replace(['Energy use (kg of oil equivalent per capita)'],'energy_use')

years_needed= []
for year in range (1995,2021):
    years_needed.append(str(year))

year_to_remove=[]

for year in range (1960, 1995):
    year_to_remove.append(str(year))

df_new= df.drop(year_to_remove, axis=1)

series_list= ["energy_use"]
df_one= df_new.loc[(df_new['Series Name'].isin(series_list))]

df_one_long= pd.melt(df_one, id_vars=["ISO", "Country"], 
                         value_vars= years_needed,
                         var_name= "Year",
                         value_name= "energy_use")

series_list= ["imports_gns", "exports_gns"]

for count, value in enumerate(series_list):
    l=[value]
    df_del= df_new.loc[(df_new['Series Name'].isin(l))]
    df_long= pd.melt(df_del, id_vars=['Country', "ISO"], 
                         value_vars= years_needed,
                         var_name= "Year",
                         value_name= value)
    df_long=df_long[[value]]
    df_one_long= pd.concat([df_one_long, df_long], axis=1, sort= False)

df_one_long= df_one_long.replace('..', np.nan, regex=False)

convert_dict = {"Year": int,
                "energy_use": float,
                "imports_gns": float,
                "exports_gns": float}

df_one_long = df_one_long.astype(convert_dict) 

df_one_long= df_one_long.drop('Country', axis=1)

df_one_long.to_csv('C:/Users/dhruv/Desktop/CS Project/import_export.csv', index= False)

