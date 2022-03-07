CREATE TABLE econ_indicators
  (Country varchar(15),
   ISO varchar(5),
   Year integer,
   GDP float,
   GDP/capita varchar(20),
   vol_imports varchar,
   vol_exports varchar,
   Population varchar);

.separator ","
.import econ_parameters_out.csv econ_indicators

CREATE TABLE climate_indicators
  (Country varchar(15),
   ISO varchar(5),
   Year integer,
   co2_emissions float,
   forest_area float,
   pm_2.5 float,
   sf6_emissions float,
   greenhouse_total float);
