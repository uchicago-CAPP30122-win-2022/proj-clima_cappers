1. Ensure that Python-3.8.5 has been installed. 


2. Run the command `bash install.sh` from inside the clima_cappers directory. The script creates a new virtual environment, 'env'; and then installs all required packages in that environment using the requirements.txt file.


3. Activate the virtual environment with the command `source env/bin/activate`. To deactivate it, type `deactivate`.


4. Launch the Dash web application from the clima_Cappers directory with the command `python3 app.py`. Once the server is running, navigate to your local webhost (e.g., `http://127.0.0.1:8000/`) in your browser of  choice (preferably Safari). The page usually takes 5-10 seconds to load due to the presence of a multiple maps and default regressions. If there is a lag in the server connection, the app will throw an error as some maps are not loaded properly. In this case, simply refresh the webpage. To stop the server at any time, press `Ctrl-Z`.


5. Optionally test the creation of the database tables. Currently, we don’t have an option that deletes the existing database. For testing the creation of the database without creating conflicts with the current database, navigate to clima_cappers/data and create a new table using create_db.sql using the command “test.sqlite3 < create-db.sql”.Then navigate to clima_cappers/ climate_indicators_api.py and update the table name in line 7 to test.sqlite3. You are ready to test the database creation process by  running the command `python3 climate_indicators_api.py from the clima_cappers.


**Description:** 
In the web interface, each layer offers different functionality to the user. In the first visual, the user may choose to compare the distribution of economic and climate indicators for a single year using the time slider at the top of the two maps. This map presents the absolute value of the indicators. The second visual offers the user an aggregated view of the indicators. Using the range slider at the top of the two maps, the user can look at the weighted average of the indicators over the selected range of years.
 
The third visual offers the consolidated performance of a country on both climate and economic indicators. The visual categorizes countries with negative emission differences and positive emission differences. Akin to the second visual, there is a range slider for this map and the user can look at the weighted average difference of emissions growth and GDP growth year for the selected years.
 
Finally, in the fourth layer of the dashboard, the default is the benchmark regression model. The user can select from a list of other explanatory variables and see the updated regression results in the table below. The user can also choose to perform the regression for the specified region. This layer also has an animated scatter plot that showcases the interaction between the variables in the benchmark model – log GDP per capita and log CO2 emissions per capita – over the given range of years.