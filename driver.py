from plant.model import SolarPlantModel
from database.database import Database

local = False
rundate = ''


plant_definition = {
	'site_nm': 'Example Site',
	'inverter_count': 5,
	'module_per_string': 10,
	'comb_per_inverter': 8,
	'combiner_count': 40,
	'albedo': 0.2,
	'surface_tilt': 20,
	'surface_azimuth': 180,
	'latitude': 34.000000,
	'longitude': -77.035787,
	'tz': 'US/Eastern',
	'module': 'First_Solar__Inv_FS_4100',
	'inverter': 'SMA_America__SC800CP_US__with_ABB_EcoDry_Ultra_transformer_',
	'catalog_id': ''
}

if local:
	rd_df = pd.read_csv('rd.csv')
else:
	rd = RunDate(local=False)
	rd_df = rd.get_sites_for_rundates(rundate)
	rd_df.to_csv('rd_df.csv', index=False)

if not rd_df.empty:
	sites = rd_df['Site'].unique()

	site_date_list = [(site, date) for site in sites for date in rd_df[rd_df['Site']==site]['RunDate'].to_list()]

	for site, date in site_date_list:
		try:
			run_daily_repor(site, date)
		except Exception as e:
			print(f"Exception caught for {site}, {date}")
			continue





