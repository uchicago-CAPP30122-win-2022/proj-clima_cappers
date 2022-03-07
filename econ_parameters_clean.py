import pandas as pd

filename = "weo2021.csv"

df = pd.read_csv(filename, encoding='windows-1252')


subject_descriptor_list= ["Gross domestic product, constant prices",
                          "Gross domestic product per capita, constant prices",
                          "Volume of imports of goods and services",
                          "Volume of exports of goods and services"]

units_list=["Percent change",
            "Purchasing power parity; 2017 international dollar"]

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
                         value_name= "Gross domestic product, constant prices")
subject_descriptor_list_new= [
                          "Gross domestic product per capita, constant prices",
                          "Volume of imports of goods and services",
                          "Volume of exports of goods and services"]

for count, value in enumerate(subject_descriptor_list_new):
    l=[value]
    df_del= df_new.loc[(df_new['Subject Descriptor'].isin(l))]
    df_long= pd.melt(df_del, id_vars=['Country', "ISO"], 
                         value_vars= years_needed,
                         var_name= "Year",
                         value_name= value)
    df_long=df_long[[value]]
    df_one_long= pd.concat([df_one_long, df_long], axis=1, sort= False)


df_one_long.to_csv('econ_parameters_out.csv')  
