import ast
import logging
import random
from optparse import make_option
import re
from django.core.management.base import BaseCommand
from businessapp.models import Product
from core.fedex.config import FedexConfig
from core.fedex.services.track_service import FedexTrackRequest
from myapp.models import Shipment
import aftership
from django.db.models import Q
from concurrent import futures
import datetime
import time
from bs4 import BeautifulSoup
import requests
import unicodedata
import urllib2
import json
import subprocess as sub


class Command(BaseCommand):
	help = 'Updates tracking info for all the services'

	option_list = BaseCommand.option_list + (
		make_option(
			"-w",
			"--workers",
			dest="workers",
			help="Number of workers",
			metavar="WRKS"
		),
	)
	option_list = option_list + (make_option("-f", action="store_true", dest="fedex"),)
	option_list = option_list + (make_option("-a", action="store_true", dest="aftership"),)
	option_list = option_list + (make_option("-e", action="store_true", dest="ecom"),)
	option_list = option_list + (make_option("-d", action="store_true", dest="dtdc"),)

	company_map = {
		'B': 'bluedart',
		'A': 'aramex',
		'DT': 'dtdc',
		'I': 'india-post'
	}
	REMOVE_LIST = ["fedex", "to fedex"]
	remove_regex = remove = '|'.join(REMOVE_LIST)
	aftership_api = aftership.APIv4('c46ba2ea-5a3e-43c9-bda6-793365ec1ebb')
	FEDEX_CONFIG_INDIA = FedexConfig(key='jFdC6SAqFS9vz7gY',
									 password='6bxCaeVdszjUo2iHw5R3tbrBu',
									 account_number='677853204',
									 meter_number='108284345',
									 use_test_server=False)
	FEDEX_CONFIG_INTRA_MUMBAI = FedexConfig(key='FRmcajHEPfMUjNmC',
                                        password='fY5ZwylNGYFXAgNoChYYYSojG',
                                        account_number='678650382',
                                        meter_number='108284351',
                                        use_test_server=False)

	FEDEX_CONFIGS = [FEDEX_CONFIG_INDIA, FEDEX_CONFIG_INTRA_MUMBAI]


	@staticmethod
	def remove_non_ascii_1(raw_text):
		return ''.join(i for i in raw_text if ord(i) < 128)


	@staticmethod
	def is_dtdc_complete(awbno):
		command = "curl 'http://dtdc.in/tracking/tracking_results.asp' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36' --data 'Ttype=awb_no&strCnno=" + str(awbno) + "'"


		import subprocess as sub

		p = sub.Popen(command,stdout=sub.PIPE,stderr=sub.PIPE,shell=True)
		output, errors = p.communicate()
		try:
			html2=output
			soup2 = BeautifulSoup(html2,'html.parser')
			try:
				return 'DELIVERED' in soup2.find("input", {"name":"cn_status"})['value']
			except:
				return False
		except:
	#		print "Unable to get the tracking webpage\n"
			#print "Status: "+r.status_code
			return False


	@staticmethod
	def make_request(awbno):
		command = "curl 'http://dtdc.in/tracking/tracking_results_detail.asp' --data 'tracktype=D&shipno=" + str(awbno) + "'"
		p = sub.Popen(command,stdout=sub.PIPE,stderr=sub.PIPE,shell=True)
		output, errors = p.communicate()
		return output

	#takes string object as param
	# return numbe of hours away from today
	@staticmethod
	def hours_gone(string_date):
		date_obj=datetime.datetime.strptime(string_date,"%Y-%m-%d %H:%M:%S")
		now=datetime.datetime.now()
		return (now-date_obj).total_seconds()//3600


	def fedex_track(self, tp):
		product, client_type = tp[0], tp[1]
		result = []
		# Set this to the INFO level to see the response from Fedex printed in stdout.
		# NOTE: TRACKING IS VERY ERRATIC ON THE TEST SERVERS. YOU MAY NEED TO USE
		# PRODUCTION KEYS/PASSWORDS/ACCOUNT #.
		# We're using the FedexConfig object from example_config.py in this dir.
		track = FedexTrackRequest(random.choice(self.FEDEX_CONFIGS))
		if product.tracking_data:
			tracking_data = ast.literal_eval(product.tracking_data)
		else:
			tracking_data = []
		original_length = len(tracking_data)
		track.TrackPackageIdentifier.Type = 'TRACKING_NUMBER_OR_DOORTAG'
		track.TrackPackageIdentifier.Value = str(product.mapped_tracking_no)

		# Fires off the request, sets the 'response' attribute on the object.
		try:
			track.send_request()

			for match in track.response.TrackDetails:
				if hasattr(match, 'ActualDeliveryTimestamp'):
					Product.objects.filter(pk=product.pk).update(status='C', actual_delivery_timestamp=match.ActualDeliveryTimestamp, estimated_delivery_timestamp=None)
				elif hasattr(match, 'EstimatedDeliveryTimestamp'):
					Product.objects.filter(pk=product.pk).update(actual_delivery_timestamp=None, estimated_delivery_timestamp=match.EstimatedDeliveryTimestamp)
				for event in match.Events:
					if event.EventType == 'RS':
						Product.objects.filter(pk=product.pk).update(status='R', return_cost=product.shipping_cost)
					if event.EventType == 'DL':
						order = product.order
						Product.objects.filter(pk=product.pk).update(status='C')
						if client_type == 'customer':
							specific_products = Shipment.objects.filter(order=order)
							order_complete = True
							for specific_product in specific_products:
								if specific_product.status == 'P':
									order_complete = False

							if order_complete:
								if client_type == 'customer':
									order.order_status = 'D'
							order.save()

					if original_length > 0:
						if tracking_data[-1]['date'] != (event.Timestamp).strftime('%Y-%m-%d %H:%M:%S'):
							if match.StatusCode == "DE":
								event_desc = "Delivery Exception (" + event.StatusExceptionDescription + ")"
							else:
								event_desc = event.EventDescription
							regex = re.compile(r'\b('+self.remove_regex+r')\b', flags=re.IGNORECASE)
							event_desc = regex.sub("", event_desc)
							if 'City' in event.Address:
								location = event.Address.City
							else:
								location = '--'
							tracking_data.append({
								"status": event_desc,
								"date": (event.Timestamp).strftime('%Y-%m-%d %H:%M:%S'),
								"location": location
							})
							Product.objects.filter(pk=product.pk).update(tracking_data=json.dumps(tracking_data))
							result = {
								"real_tracking_no": product.real_tracking_no,
								"company": 'fedex',
								"tracking_no": product.mapped_tracking_no,
								"updated": True,
								"error": False
							}
						else:
							hours=self.hours_gone(tracking_data[-1]['date'])
							if "Shipment information sent" in tracking_data[-1]['status']:
								if (hours>12):
									Product.objects.filter(pk=product.pk).update(warning=True, warning_type='FSI')
								if (hours>24):
									Product.objects.filter(pk=product.pk).update(warning=True, warning_type='F24')



							result = {
								"real_tracking_no": product.real_tracking_no,
								"company": 'fedex',
								"tracking_no": product.mapped_tracking_no,
								"updated": False,
								"error": False
							}
					else:
						if match.StatusCode == "DE":
							event_desc = "Delivery Exception (" + event.EventDescription + ")"
						else:
							event_desc = event.EventDescription
						regex = re.compile(r'\b('+self.remove_regex+r')\b', flags=re.IGNORECASE)
						event_desc = regex.sub("", event_desc)
						if 'City' in event.Address:
							location = event.Address.City
						else:
							location = '--'
						tracking_data.append({
							"status": event_desc,
							"date": (event.Timestamp).strftime('%Y-%m-%d %H:%M:%S'),
							"location": location
						})
						Product.objects.filter(pk=product.pk).update(tracking_data=json.dumps(tracking_data))
						result = {
							"real_tracking_no": product.real_tracking_no,
							"company": 'fedex',
							"tracking_no": product.mapped_tracking_no,
							"updated": True,
							"error": False
						}
		except Exception,e:
			result = {
				"real_tracking_no": product.real_tracking_no,
				"company": 'fedex',
				"tracking_no": product.mapped_tracking_no,
				"updated": False,
				"error": str(e)
			}
		return result

	def aftership_track(self, tp):
		coin_flip = random.choice([True, False])
		if coin_flip:
			time.sleep(1)
		product, client_type = tp[0], tp[1]
		tracking_data = []
		company = self.company_map[product.company]
		try:
			self.aftership_api.trackings.post(
				tracking=dict(slug=company, tracking_number=product.mapped_tracking_no, title="Title"))
			data = self.aftership_api.trackings.get(company, product.mapped_tracking_no, fields=['checkpoints'])
		except:
			data = self.aftership_api.trackings.get(company, product.mapped_tracking_no, fields=['checkpoints'])

		if data:
			result = {
				"company": company,
				"tracking_no": product.mapped_tracking_no,
				"updated": True,
				"error": False
			}
		else:
			result = {
				"company": company,
				"tracking_no": product.mapped_tracking_no,
				"updated": False,
				"error": True
			}
		for x in data['tracking']['checkpoints']:
			y1 = str(x['checkpoint_time'])
			str1 = y1.decode("windows-1252")
			str0 = self.remove_non_ascii_1(x['message'])
			str3 = x['location'].encode('utf8')
			tracking_data.append({"status": str(str0), "date": str(str1), "location": str(str3)})

			if 'shipment returned back to shipper'.lower() in str0.lower():
				Product.objects.filter(pk=product.pk).update(status='R', return_cost=product.shipping_cost)

			if 'delivered' in str0.lower():
				Product.objects.filter(pk=product.pk).update(status='C')
				order = product.order
				# getting all products of that order

				if client_type == 'customer':
					specific_products = Shipment.objects.filter(order=order)
					order_complete = True
					for specific_product in specific_products:
						if specific_product.status == 'P':
							order_complete = False

					if order_complete:
						if client_type == 'customer':
							order.order_status = 'D'
						order.save()

				break

		if json.dumps(tracking_data) != '[]':
			Product.objects.filter(pk=product.pk).update(tracking_data=json.dumps(tracking_data))
		return result




	def ecom_track(self,tp):
		product, client_type = tp[0], tp[1]
		company='Ecom'
		completed=False
		returned = False
		tracking_data=[]
		url='https://billing.ecomexpress.in/track_me/multipleawb_open/?awb='+str(product.mapped_tracking_no)+'&order&news_go=track+now'
		try:
			soup = BeautifulSoup(urllib2.urlopen(url).read())
			col = [i.string.encode('utf-8').strip().replace('\xc2\xa0\xc2\xa0\xc2\xa0', "") for i in soup('td') if i.string != None and i.parent.a == None]
			del col[0]

			data =[]
			date = []
			new_data = []
			exp_date = [] #This variable stores the ETA of packages
			s = 0
			a = 0
			b = 0
			c = 0

			while s+2 < len(col): #This loop is used to split the date and location
				date.append(col[s+1].split(','))
				s += 2

			while a < len(date): #This adds all the items to the list
				data.append(date[a][0].strip()), data.append(date[a][1].strip()), data.append(col[b])
				exp_date.append(date[a][0])
				b += 2
				a += 1

			while c < len(data):
				new_data.append({"status" : data[c + 2], "date" : data[c],"location": data[c + 1] })
				if "delivered" in str(data[c + 2]).lower():
					if "undelivered" not in str(data[c + 2]).lower():
						completed=True
				c += 3


			# new_tracking = sorted(new_data, key=lambda k: k["date"])
			tracking_data=new_data[::-1]

			# for row in new_tracking:
			#     tracking_data.append(row)
				# if "delivered" in row["status"].lower():
				#     completed=True


			x=soup.findAll(attrs={'class': re.compile(r".*\btmargin10\b.*")})
			if "shipment redirected" in x[-1].text.lower():
				returned = True


			result = {
				"company": company,
				"tracking_no": product.mapped_tracking_no,
				"updated": True,
				"error": False
			}

		except Exception as e:
			result = {
				"company": company,
				"tracking_no": product.mapped_tracking_no,
				"updated": False,
				"error": str(e)
			}

		if json.dumps(tracking_data) != '[]':
			Product.objects.filter(pk=product.pk).update(tracking_data=json.dumps(tracking_data))

		if (returned):
			Product.objects.filter(pk=product.pk).update(status='R', return_cost=product.shipping_cost)

		if (completed):
			Product.objects.filter(pk=product.pk).update(status='C')
			order = product.order
			# getting all products of that order

			if client_type == 'customer':
				specific_products = Shipment.objects.filter(order=order)
				order_complete = True
				for specific_product in specific_products:
					if specific_product.status == 'P':
						order_complete = False

				if order_complete:
					if client_type == 'customer':
						order.order_status = 'D'
					else:
						order.status = 'C'
					order.save()


		return result

	def dtdc_track(self,tp):

		product, client_type = tp[0], tp[1]
		company='Dtdc'
		completed=False
		tracking_data=[]
		patt = re.compile('(\s*)DTDC')
		try:
			html = self.make_request(str(product.mapped_tracking_no))
			if(html != "error"):
				soup = BeautifulSoup(html,'html.parser')

				#print soup

				all_the_tables = soup.find_all(id="box-table-a")
				tracking_table = all_the_tables[2]
				#print all_the_tables[1]


				tracking_data = []
				table_rows = tracking_table.find_all('tbody')[0].find_all('tr')


				for row in table_rows:
					#print  encode_contents(row.get('class'))
					rowClass = unicodedata.normalize('NFKD', row.get('class')[0]).encode('ascii','ignore')
					if(rowClass=='altRow'):
						date = row.find('strong').text
					if(rowClass == 'divider'):
						row_td = row.find_all('td')
						status = patt.sub('', row_td[0].text)
						location = row_td[1].text
						time = date + row_td[2].text
						tracking_data.append({'status':status,'location':location,'date':time})

				# print json.dumps(tracking_data)

				# for row in new_tracking:
				#     tracking_data.append(row)
					# if "delivered" in row["status"].lower():
					#     completed=True

				result = {
					"company": company,
					"tracking_no": product.mapped_tracking_no,
					"updated": True,
					"error": False
				}

		except Exception as e:
			result = {
				"company": company,
				"tracking_no": product.mapped_tracking_no,
				"updated": False,
				"error": str(e)
			}

		completed=self.is_dtdc_complete(product.mapped_tracking_no)

		if json.dumps(tracking_data) != '[]':
			Product.objects.filter(pk=product.pk).update(tracking_data=json.dumps(tracking_data))


		if (completed):
			#Product.objects.filter(pk=product.pk).update(status='C')
			order = product.order
			# getting all products of that order
			temp_obj=Product.objects.get(pk=product.pk)
			tracking_data=json.loads(temp_obj.tracking_data)
			tracking_data.append({
								"status": 'Delivered',
								"date": (datetime.datetime.now()).strftime('%Y-%m-%d %H:%M:%S'),
								"location": "recipient city"
							})
			Product.objects.filter(pk=product.pk).update(status='C',tracking_data=json.dumps(tracking_data))

			if client_type == 'customer':
				specific_products = Shipment.objects.filter(order=order)
				order_complete = True
				for specific_product in specific_products:
					if specific_product.status == 'P':
						order_complete = False

				if order_complete:
					if client_type == 'customer':
						order.order_status = 'D'
					else:
						order.status = 'C'
					order.save()

		return result

#parser("https://billing.ecomexpress.in/track_me/multipleawb_open/?awb=122066652&order&news_go=track+now")



	def handle(self, *args, **options):

		dtdc_track_queue = []
		# Track Bluedart shipments for businesses and customers
		dtdc_business_shipments = Product.objects.filter(
			(Q(company='DT')) & (
				Q(status='P') | Q(status='DI'))).exclude(Q(order__status='C')| Q(order__status='N'))

		for dtdc_business_shipment in dtdc_business_shipments:
			dtdc_track_queue.append((dtdc_business_shipment, 'business'))

		dtdc_customer_shipments = Shipment.objects.filter(
			( Q(company='DT')) & (
				Q(status='P') | Q(status='DI'))).exclude( Q(order__order_status='N')| Q(order__order_status='D'))

		for dtdc_customer_shipment in dtdc_customer_shipments:
			dtdc_track_queue.append((dtdc_customer_shipment, 'customer'))


		ecom_track_queue = []
		# Track Bluedart shipments for businesses and customers
		ecom_business_shipments = Product.objects.filter(
			(Q(company='E')) & (
				Q(status='P') | Q(status='DI'))).exclude(Q(order__status='C')| Q(order__status='N'))

		for ecom_business_shipment in ecom_business_shipments:
			ecom_track_queue.append((ecom_business_shipment, 'business'))

		ecom_customer_shipments = Shipment.objects.filter(
			( Q(company='E')) & (
				Q(status='P') | Q(status='DI'))).exclude( Q(order__order_status='N')| Q(order__order_status='D'))

		for ecom_customer_shipment in ecom_customer_shipments:
			ecom_track_queue.append((ecom_customer_shipment, 'customer'))


		aftership_track_queue = []
		# Track Bluedart shipments for businesses and customers
		aftership_business_shipments = Product.objects.filter(
			(Q(company='B') | Q(company='A') | Q(company='I')) & (
				Q(status='P') | Q(status='DI'))).exclude(Q(order__status='C')| Q(order__status='N'))

		for aftership_business_shipment in aftership_business_shipments:
			aftership_track_queue.append((aftership_business_shipment, 'business'))

		aftership_customer_shipments = Shipment.objects.filter(
			(Q(company='B') | Q(company='A') |  Q(company='I')) & (
				Q(status='P') | Q(status='DI'))).exclude( Q(order__order_status='N')| Q(order__order_status='D'))

		for aftership_customer_shipment in aftership_customer_shipments:
			aftership_track_queue.append((aftership_customer_shipment, 'customer'))


		fedex_track_queue = []
		fedex_business_shipments = Product.objects.filter(Q(company='F') & (Q(status='P') | Q(status='DI'))).exclude(Q(order__status='C')| Q(order__status='N'))

		for fedex_business_shipment in fedex_business_shipments:
			fedex_track_queue.append((fedex_business_shipment, 'business'))

		fedex_customer_shipments = Shipment.objects.filter(Q(company='F') & (Q(status='P') | Q(status='DI'))).exclude( Q(order__order_status='N')| Q(order__order_status='D'))

		for fedex_customer_shipment in fedex_customer_shipments:
			fedex_track_queue.append((fedex_customer_shipment, 'customer'))

		if options['workers'] is None:
			workers = 1
		else:
			workers = int(options['workers'])

		if options['fedex']:
			if len(fedex_track_queue) > 0:
				with futures.ThreadPoolExecutor(max_workers=workers) as executor:
					futures_track = (executor.submit(self.fedex_track, item) for item in fedex_track_queue)
					for result in futures.as_completed(futures_track):
						if result.exception() is not None:
							print('%s' % result.exception())
						else:
							print(result.result())
				print("Starting fedex order save..")
				for fedex_product in fedex_business_shipments:
					try:
						fedex_product.order.save()
						print("Fedex saving order {}".format(fedex_product.order.order_no))
					except Exception as e:
						print(str(e))
						print("Error in {}".format(fedex_product.real_tracking_no))
				print("Fedex order save complete")
		elif options['aftership']:
			if len(aftership_track_queue) > 0:
				with futures.ThreadPoolExecutor(max_workers=5) as executor:
					futures_track = (executor.submit(self.aftership_track, item) for item in aftership_track_queue)
					for result in futures.as_completed(futures_track):
						if result.exception() is not None:
							print('%s' % result.exception())
						else:
							print(result.result())
				print("Starting aftership order save..")
				for aftership_product in aftership_business_shipments:
					try:
						aftership_product.order.save()
						print("Afteship saving order {}".format(aftership_product.order.order_no))
					except Exception as e:
						print(str(e))
						print("Error in {}".format(aftership_product.real_tracking_no))
				print("Aftership order save complete")
		elif options['ecom']:
			if len(ecom_track_queue) > 0:
				with futures.ThreadPoolExecutor(max_workers=workers) as executor:
					futures_track = (executor.submit(self.ecom_track, item) for item in ecom_track_queue)
					for result in futures.as_completed(futures_track):
						if result.exception() is not None:
							print('%s' % result.exception())
						else:
							print(result.result())
				print("Starting ecom order save..")
				for ecom_product in ecom_business_shipments:
					try:
						ecom_product.order.save()
						print("Ecom saving order {}".format(ecom_product.order.order_no))
					except Exception as e:
						print(str(e))
						print("Error in {}".format(ecom_product.real_tracking_no))
				print("Ecom order save complete")
		elif options['dtdc']:
			if len(dtdc_track_queue) > 0:
				with futures.ThreadPoolExecutor(max_workers=workers) as executor:
					futures_track = (executor.submit(self.dtdc_track, item) for item in dtdc_track_queue)
					for result in futures.as_completed(futures_track):
						if result.exception() is not None:
							print('%s' % result.exception())
						else:
							print(result.result())
				print("Starting dtdc order save..")
				for dtdc_product in dtdc_business_shipments:
					try:
						dtdc_product.order.save()
						print("DTDC saving order {}".format(dtdc_product.order.order_no))
					except Exception as e:
						print(str(e))
						print("Error in {}".format(dtdc_product.real_tracking_no))
				print("DTDC order save complete")
		else:

			if len(aftership_track_queue) > 0:
				with futures.ThreadPoolExecutor(max_workers=5) as executor:
					futures_track = (executor.submit(self.aftership_track, item) for item in aftership_track_queue)
					for result in futures.as_completed(futures_track):
						if result.exception() is not None:
							print('%s' % result.exception())
						else:
							print(result.result())
				print("Starting aftership order save..")
				for aftership_product in aftership_business_shipments:
					try:
						aftership_product.order.save()
						print("Afteship saving order {}".format(aftership_product.order.order_no))
					except Exception as e:
						print(str(e))
						print("Error in {}".format(aftership_product.real_tracking_no))
				print("Aftership order save complete")

			if len(fedex_track_queue) > 0:
				with futures.ThreadPoolExecutor(max_workers=workers) as executor:
					futures_track = (executor.submit(self.fedex_track, item) for item in fedex_track_queue)
					for result in futures.as_completed(futures_track):
						if result.exception() is not None:
							print('%s' % result.exception())
						else:
							print(result.result())

				print("Starting fedex order save..")
				for fedex_product in fedex_business_shipments:
					try:
						fedex_product.order.save()
						print("Fedex saving order {}".format(fedex_product.order.order_no))
					except Exception as e:
						print(str(e))
						print("Error in {}".format(fedex_product.real_tracking_no))
				print("Fedex order save complete")

			if len(ecom_track_queue) > 0:
				with futures.ThreadPoolExecutor(max_workers=workers) as executor:
					futures_track = (executor.submit(self.ecom_track, item) for item in ecom_track_queue)
					for result in futures.as_completed(futures_track):
						if result.exception() is not None:
							print('%s' % result.exception())
						else:
							print(result.result())
				print("Starting ecom order save..")
				for ecom_product in ecom_business_shipments:
					try:
						ecom_product.order.save()
						print("Ecom saving order {}".format(ecom_product.order.order_no))
					except Exception as e:
						print(str(e))
						print("Error in {}".format(ecom_product.real_tracking_no))
				print("Ecom order save complete")


			if len(dtdc_track_queue) > 0:
				with futures.ThreadPoolExecutor(max_workers=workers) as executor:
					futures_track = (executor.submit(self.dtdc_track, item) for item in dtdc_track_queue)
					for result in futures.as_completed(futures_track):
						if result.exception() is not None:
							print('%s' % result.exception())
						else:
							print(result.result())
				print("Starting dtdc order save..")
				for dtdc_product in dtdc_business_shipments:
					try:
						dtdc_product.order.save()
						print("DTDC saving order {}".format(dtdc_product.order.order_no))
					except Exception as e:
						print(str(e))
						print("Error in {}".format(dtdc_product.real_tracking_no))
				print("DTDC order save complete")