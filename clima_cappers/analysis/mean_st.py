import pandas as pd
filename = "C:/Users/dhruv/Desktop/CS Project/Mean_Global_Surface_Temperature.csv"

df = pd.read_csv(filename)
df_new= df.drop(["ObjectId",
                     "ISO2",
                     "Indicator",
                     "Code",
                     "Unit"
                     ], axis=1)

df_new.columns = df_new.columns.str.replace('[F]', '')

years_needed= []
for year in range (1995,2020):
    years_needed.append(str(year))
    
df_one_long= pd.melt(df_new, id_vars=["ISO3", "Country"], 
                         value_vars= years_needed,
                         var_name= "Year",
                         value_name= "mean_st")

df_one_long.to_csv('C:/Users/dhruv/Desktop/CS Project/mean_st_output.csv', index= False,)  