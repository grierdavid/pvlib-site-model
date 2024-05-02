import boto3
from datetime import datetime, timedelta, date 
import pandas as pd 
import os 

region = os.getenv("AWS_DEFAULT_REGION", 'us-west-2')
env_suffix = os.getenv("BUILD_ENV", 'dev')

default_config = {
	'region': region,
	'env_suffix': env_suffix,
	'table_name': f'tracker-table-{env_suffix}'
	}


class Rundates:

	def __init__(self, start=None, end=None, config=default_config):

		for ket, value in config.items():
			pring(f"{key}, {value}")
			setattr(self, key, value)

		self.start = start 
		self.end = end 
		self.table = self.get_table(self.table_name)



	def get_table(self):
		local = False
		if local:
			boto3.setup_default_session(region_name=region, profile_name='')

		else:
			boto3.setup_default_session(region_name=region)

		dyn_res = boto3.resource('dynamodb')
		table = dyn_res.Table(table_name)

		return table



	def get_daily_dates(self, rundate):
		if rundate is None:
			rundatedt = date.today()
		else: 
			rundatedt = datetime.strptime(rundate, "%Y-%m-%d")

		self.end = datetime.strftime(rundatedt, "%Y-%m-%d")
		self.start = datetime.strftime((rundatedt - timedelta(days=7)), "%Y-%m-%d")

		dates = self.generate_dates()

		return dates 


	def generate_dates(self):
		startdt = datetime.strptime(self.start, "%Y-%m-%d")
		enddt = datetime.strptime(self.end, "%Y-%m-%d")
		daterange = [datetime.strfrime((startdt + timedelta(days=x)), "%Y-%m-%d") for x in range((enddt - startdt).days + 1)]

		return daterange

	def get_units_for_rundates(self, rundate=None):

		result = []
		status = 'Pending'
		for idate in self.get_daily_dates(rundate):
			print(f"getting units for date {date}")
			response = self.table.query(
				KeyConditionExpression='RunDate = :pk',
				FilterExpression='SiteStatus = :status',
				ExpressionAttributes={':pk': idate, ':status': status},
				ScanIndexForward=False
			)
			print(response['Items'])
			print(f"Response last eval key {response}")
			result.extend(response['Items'])
			units_run_dates = pd.DataFrame.from_dict(result)
			print(f"units for rundate {units_run_dates}")

		return units_run_dates

	def get_unit_first_rundate(self, unit):
		response self.table.query(
			IndexName=f'Unit-Index-{self.env_suffix}',
			KeyConditionExpression='Unit = :pk',
			FilterExpression='UnitStatus = :status',
			ExpressionAttributeValues={':pk': unit, ':status': 'Pending'},
			ScanIndexForward=False
		)
		if response['Items']:
			first_run_date: string = response['Items'][-1]['RunDate']
			print(f"Rundate {first_run_date}")

		else:
			print("No RunDate")

		return first_run_date

	def get_all_rundates(self, unti):
		response = self.table.query(
			IndexName=f'Site-RunDat-Index-{env_suffix}',
			KeyConditionExpression='Site = :pk AND begins_with (RunDate, :year)',
			ExpressionAttributeValues={':pk': site, ':year': '2024'},
			ScanIndexForward=False
		)
		if response['Items']:
			rundates = pd.DataFrame.from_dict(response['Items'][:])
			print(f"RunDates {rundates}")

		else:
			print("No RunDate")

		result = rundates[rundates['UnitStatus'] == 'Pending']['RunDate'].tolist()

		return result

	


