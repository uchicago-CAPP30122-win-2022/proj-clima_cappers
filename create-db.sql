CREATE TABLE econ_indicators
  (country varchar(15),
   iso_code varchar(5),
   year integer,
   gdp float,
   gdp_capita float,
   vol_imports float,
   vol_exports float,
   population float,
   PRIMARY KEY (iso_code, year));

.separator ","
.import econ_parameters_out.csv econ_indicators

CREATE TABLE mean_temp_indicator
(country varchar(15),
  iso_code varchar(5),
  year integer,
  mean_temp float,
  PRIMARY KEY (iso_code, year));

.separator ","
.import mean_st_output.csv mean_temp_indicator

CREATE TABLE climate_indicators
  (country varchar(15),
   iso_code varchar(5),
   year integer,
   gdp_capita float,
   gini_index float,
   co2_emissions_kt float,
   co2_emissions_capita float,
   forest_area float,
   population_total float,
   electricity_pro_hydro float,
   electricity_pro_natural_gas float,
   electricity_pro_nuclear float,
   electricity_pro_oil float,
   electricity_pro_coal float,
   electricity_pro_fossils float,
   electricity_pro_renewable float,
   pm_25 float,
   sf6_emissions float,
   ghg_total float,
   ghg_growth float,
   ghg_capita float,
   exports_gns float,
   imports_gns floats,
   PRIMARY KEY (iso_code, year));
