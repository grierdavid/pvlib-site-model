import pvlib
import pandas as pd 
import datetime
from pvlib.pvsystem import PVSystem, retrieve_sam
from pvlib.modelchain import ModelChain 
from pvlib import irradiance
from forecast.forecast import NAM


import boto3
import awswrangler as wr 

Local = True
if Local:
	boto3.setup_default_session(region_name='us-west-2')
else:
	boto3.setup_default_session(region_name='us-west-2')

site_def: dict[str, int | float | str ] = {
	'inverter_count': 85,
	'module_per_string': 15,
	'string_per_combiner': 15,
	'comb_per_inv': 12.9,
	'albedo': 0.2,
	'surface_tilt': 20,
	'surface_azimuth': 180,
	'altitude': '',
	'latitude': 35.005494,
	'longitude': -78.125956,
	'tz': 'US/Eastern',
	'tracker_site': False,
	'module': 'First_Solar__Inc__FS_4100',
	'inverter': 'SMA_America__SC800CP_US__with_ABB_EcoDry_Ultra_transformer_',
	'poa_input': ''
}





class SolarPlantModel:
	def __init__(self, config=site_def):
		print(site_def)
		self.start= None
		self.end = None
		for key, value in site_def.items():
			print(f"setting {key}:self.{value}")
			setattr(self, key, value)

		self.site = self.get_location()
		self.times = self.get_times()
		self.poa_weather = None


	def get_location(self):
		site = pvlib.location.Location(self.latitude, self.longitude)
		return site 

	def get_times(self):
		today = pd.Timestamp(datetime.date.today(), tz=self.tz)
		if self.start is None:
			self.start = today - pd.Timedelta(days=1)

		if self.end is None:
			self.end = today

		print(f"start: {self.start} end: {self.end}")
		times = pd.date_range(start=self.start, end=self.end, freq='6min', tz=self.tz)
		return times

		


	def get_sun_rise_set(self):
		sun_rise_set = self.get_sun_rise_set_transits(self.times)
		sunrise = sun_rise_set['sunrise'].min()
		sunset = sun_rise_set['sunset'].min()

		return sunrise, sun_set 

	def get_clearsky(self):
		clearsky = self.site.get_clearsky(self.times)
		#sunrise, sunset = self.get_sun_rise_set()
		#clearsky_filtered = clearsky[(clearsky.index >= sunrise) & (clearsky.index <= sunset)]
		return clearsky

	def get_irradiance(self):
		clearsky = self.get_clearsky()
		solpos = pvlib.solarposition.get_solarposition(self.times, self.site.latitude, self.site.longitude)
		airmass = pvlib.atmosphere.get_relative_airmass(solpos['apparent_zenith'])
		pressure = pvlib.atmosphere.alt2pres(self.site.altitude)
		am_abs = pvlib.atmosphere.get_absolute_airmass(airmass, pressure)

		solar_position = self.site.get_solarposition(self.times)

		aoi = pvlib.irradiance.aoi(self.surface_tilt, self.surface_azimuth,
			solpos['apparent_zenith'], solpos['azimuth'])

		poa_irradiance = irradiance.get_total_irradiance(
			surface_tilt=self.surface_tilt,
			surface_azimuth=self.surface_azimuth,
			dni=clearsky['dni'],
			ghi=clearsky['ghi'],
			dhi=clearsky['dhi'],
			solar_zenith=solar_position['apparent_zenith'],
			solar_azimuth=solar_position['azimuth'],
			albedo=self.albedo
			)

		return poa_irradiance

	def get_site_poa(self):
		db = ''
		table = ''
		sql = f""

		try:
			result = self.run_query()
		except Exception as e:
			print(f"exception: {e}")



	def get_lakeformation_data(self, db, cat_id):
		return 


	def get_clearsky_forecast_weather(self):
		fm = NAM()
		data = fm.get_data(self.latitude, self.longitude, self.start, self.end)
		processed_data = fm.process_data(data)
		#nam_filtered = processed_data[(processed_data.index >= sunrise) & (processed_data.index <= sunset)]
		nam_6m = processed_data.resample('6T').asfreq()
		nam_6m_fill = nam_6m.ffill()
		clearsky  = self.get_clearsky()
		weather = pd.DataFrame(
			{
				'temp_air': nam_6m_fill['temp_air'],
				'wind_speed': nam_6m_fill['wind_speed'],
				'dni': clearsky['dni'],
				'ghi': clearsky['ghi'],
				'dhi': clearsky['dhi']
			}
		)

		return weather

	def get_site_poa_forecast_weather(self):
		fm = NAM()
		data = fm.get_data(self.latitude, self.longitude, self.start, self.end)
		processed_data = fm.process_data(data)

		nam__6m = processed_data.resample('6min').asfreq()
		nam_6m_fill = nam_6m.ffill()
		site_poa, site_poa_filtered = self.get_site_poa()

		weather = pd.DataFrame(
			{
				'temp_air': nam_6m_fill['temp_air'],
				'wind_speed': nam_6m_fill['wind_speed'],
				'poa_global': site_poa
			}
		)

		return weather

	def get_inverter_module_cec(self):
		cec_modules = retrieve_sam('CECMod')
		cec_inverters = retrieve_sam('cecinverter')

		module_params = cec_modules[self.module]
		inverter_params = cec_inverters[self.inverter]

		return module_params, inverter_params

	def get_thermal_params(self):
		thermal_params = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']
		if self.poa_weather is None:
			poa_irradiance = self.get_irradiance()
			clearsky_weather = self.get_clearsky_forecast_weather()
			temps = pvlib.temperature.sapm_cell(poa_irradiance['poa_global'], clearsky_weather['temp_air'], clearsky_weather['wind_speed'], **thermal_params)
		else:
			poa_weather = model.get_site_poa_forecast_weather()
			temps = pvlib.temperature.sapm_cell(poa_weather['poa_global'], poa_weather['temp_air'], poa_weather['wind_speed'], **thermal_params)


		return temps, thermal_params


	def get_pvsystem(self, inverter_params, module_params, temps, thermal_params):
		strings_per_inverter = self.string_per_combiner * self.comb_per_inv

		system = PVSystem(
			surface_tilt=self.surface_tilt,
			surface_azimuth=self.surface_azimuth,
			module_parameters=module_params,
			inverter_parameters=inverter_params,
			temperature_model_parameters=thermal_params,
			albedo=self.albedo,
			surface_type=None,
			module='FS_4100',
			module_type='glass_polymer',
			modules_per_string=self.module_per_string,
			strings_per_inverter=strings_per_inverter,
			inverter='SMA_SC800CP_US',
			racking_model='open_rack',
			losses_parameters=None,
			name='PV System'
			)

		return system


	def get_model_chain(self, system):

		mc = ModelChain(system, self.site, name='Plant',
		transposition_model='haydavies',solar_position_method='nrel_numpy',
		airmass_model='kastenyoung1989',dc_model=None,ac_model=None, aoi_model='no_loss',spectral_model='no_loss',
		temperature_model='sapm', losses_model='no_loss')

		return mc