import boto3
import os
import logging
from datetime import datetime, timedelta, date
from pandas import pd
from awswrangler import wr

logging.basicConfig(level=logging.DEBUG)

region = os.getenv("AWS_DEFAULT_REGION", 'us-west-2')
env_suffix = os.getenv("BUILD_ENV", 'dev')
acct_id = os.getenv("AWS_ACCOUNT_ID", '')
anthena_output_bucket = os.getenv("ATHENA_OUTPUT_BUCKET")
anthena_output_bucket_path = os.getenv("ATHENA_OUTPUT_PATH")



local = False

if local:
	boto3.setup_default_session(region_name=region, profile_name='')
else:
	boto3.setup_default_session(region_name=region)

default_config = {
			'raw_db': '',
			'dim_db': '',
			'stage_db': '',
			'env': '',
			'region': f'{region}',
			'tz': 'US/Eastern',
			'athena_output': f's3://{anthena_output_bucket}/{anthena_output_bucket_path}',
			'athena_workgroup': 'primary',
			'catalog_id': acct_id
			}

site_list = []


class Database:

	def __init__(self, site, rundate=None, sbx=False, config=default_config):

		for key, value in config.items():
			print(f"{key}: {value}")
			setattr(self, key, value)

		self.site: string = site
		self.sbx = sbx
		self.rundate = rundate




	def athena_query(self, db, sql):
		print(f"Runnint SQL {sql}")
		df_dim = wr.athena.read_sql_query(
			sql=sql,
			database=db,
			workgroup=self.athena_workgroup,
			s3_output=self.anthena_output 
		)
		return df_dim


	def get_site_inverter_map(self):
		sql = f"""
			SELECT * FROM "site_inverter_map"
			"""

		result. = self.athena_query(self.dim_db, sql)


	def get_times(self):
		start, end, startstr, endstr = self.get_start_end():

		print(self.start)
		print(self.end)
		times = pd.date_range(start=start, end=end, freq='6min', tz=self.tz)
		return times

    def get_start_end(self):
    	base_format = '%Y-%m-%d'
    	if self.rundate is not None:
    		startdt = pd.Timestamp(datetime.strptime(self.rundate, base_format), tz=self.tz)
    	else:
    		try:
    			startdt = pd.Timestamp(datetime.today(), tz=self.tz)

    		except Exception as e:
    			print(f"set start time error {e}")


    	try:
    		enddt = pd.Timestamp(datetime.strftime(start_dt + timedelta(days=1), base_format), tz=self)
    	except Exception as e:
    		print(f"set end time exception {e}")

    	print(startdt)
    	print(enddt)

    	startsrt = datetime.strftime(startdt, base_format)
    	endstr = datetime.strftime(enddt, base_format)

    	return startdt, enddt, startstr, endstr


    def localize_data(self, data):
    	data.index = pd.to_datetime(data.index)
    	data.index = data.index.tz_localize('UTC').tz_convert(self.tz)
    	startdt, enddt, startstr, endstr = self.get_start_end()
    	day_data = data[startdt:enddt]

    	return day_data


   




			)
