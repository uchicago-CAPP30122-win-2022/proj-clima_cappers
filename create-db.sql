CREATE TABLE econ_indicators
  (country varchar(15),
   iso_code varchar(5),
   year integer,
   gdp float,
   gdp_capita float,
   vol_imports float,
   vol_exports float,
   population float);

.separator ","
.import econ_parameters_out.csv econ_indicators

CREATE TABLE climate_indicators
  (country varchar(15),
   iso_code varchar(5),
   year integer,
   co2_emissions float,
   forest_area float,
   pm_25 float,
   sf6_emissions float,
   greenhouse_total float);
